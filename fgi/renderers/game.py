# -*- coding: utf-8 -*-

# 
# Copyright (C) 2020 Utopic Panther
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 

import os
import re
from html import escape

from fgi.base import make_wrapper
from fgi.renderer import Renderer
from fgi.link import link_info
from fgi.seo import keywords
from fgi.misc.icon import platform_icons

class RendererGame(Renderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.basectx = {
            "rr": "../..",
            "link_info": make_wrapper(link_info, self.fctx),
            "platform_icons": platform_icons
        }

        self.games = self.lctx["games"]
        self.authors = self.lctx["authors"]
        self.context = self.new_context()

        lang_without_region = self.language
        if '-' in lang_without_region:
            lang_without_region = lang_without_region.split('-')[0]

        self.context["lang_without_region"] = lang_without_region

    def new_game_context(self):
        return self.context.copy()

    def author_widget(self, game):
        name = game.id
        data = {}
        ga = {}

        for author in game.authors:
            aname = author["name"]
            if aname in self.authors:
                tmp = self.authors[aname]["games"]

                for g in tmp:
                    i = g.id
                    if i != name:
                        if i not in ga:
                            ga[i] = set()
                        ga[i].add(aname)

        for gid, au in ga.items():
            authornames = ", ".join(sorted(au))
            if authornames not in data:
                data[authornames] = []
            data[authornames].append(self.games[gid])

        return data

    def render_game(self, gid, game):
        print("  => %s" % gid)
        context = self.new_game_context()

        context["game"] = game
        context["name"] = gid
        context["author_widget"] = self.author_widget(game)

        if game.expunge:
            context["noindex"] = True

        meta = dict()
        meta["title"] = game.get_name(self.language)
        meta["description"] = escape(game.get_description(self.language).text[:200].replace('\n', '') + "...")
        meta["image"] = game.thumbnail.with_rr(context["rr"]).src
        meta["extra_keywords"] = keywords.game_page_extra_keywords(game, context["ui"])
        context["meta"] = meta

        return self.env.get_template("game.html").render(context)

    def render(self):
        for gid, game in self.games.items():
            with self.sm_openw("games", gid + ".html", sm = not game.expunge,
                    priority="0.7", lastmod_ts=game.get_mtime(self.language)) as f:
                f.write(self.render_game(gid, game))

impl = RendererGame
