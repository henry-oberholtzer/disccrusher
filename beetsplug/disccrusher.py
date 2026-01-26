from __future__ import annotations

from functools import cached_property

from beets.plugins import BeetsPlugin
from beets.autotag.hooks import AlbumInfo
from beets import ui
from beets.library.models import Album

# If the incoming data is set to a specified type, crush the number of discs to 1
# Everything should be numbered in order.

class DiscCrusher(BeetsPlugin):
    def __init__(self) -> None:
        super().__init__()


        self.config.add({
            "crush": ["Vinyl"]
        })

        self._command = ui.Subcommand(
            "crush",
            help="Crush and albums discs to one."
        )

        self.register_listener(
                "albuminfo_received", self.crush_discs
        )

    @cached_property
    def to_crush(self) -> set[str]:
        return set([s.upper() for s in self.config["crush"].as_str_seq()])

    def crush_discs(self, info: AlbumInfo | Album):
        # For each album, set "disctotal" to 1
        if isinstance(info, AlbumInfo):
            self._log.debug(f"crushing {info.album}")
            if info.media.upper() in self.to_crush:
                info.mediums = 1
                for track in info.tracks:
                # Set new index
                    track.medium_index = track.index
                # Set disc to 1
                    track.medium = 1
                # Set disc total to 1
                    track.medium_total = 1
                    self._log.debug(f"setting {track.title} to {track.medium}-{track.medium_index}/{track.medium_total}")
        elif isinstance(info, Album):
            items = info.items()
            media = set([i.media.upper() for i in items])
            if len(media) == 1 and media in self.to_crush:
                info.disctotal = 1
                for i, item in enumerate(items):
                    item.disctotal = 1
                    item.disc = 1
                    item.track = (i + 1)
                    self._log.debug(f"setting {item.title} to {item.disc}-{item.track}/{item.disctotal}")

    def commands(self) -> list[ui.Subcommand]:
        def func(lib, opts, args):
            for item in lib.albums(args):
                initial_discs = item.disctotal
                if initial_discs <= 1:
                    self._log.info(f"no discs to crush on {item.album}")
                    continue
                else:
                    self.crush_discs(item)
                    item.store()
                    remaining_discs = item.disctotal
                    item.try_sync(write=True, move=True)
                    self._log.info(f"crushed {item.album}'s {initial_discs} discs to {remaining_discs}")

        self._command.func = func
        return [self._command]


