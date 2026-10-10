from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "cytometry_search": "./js/cytometry/search/index.js",
                "cytometry_deposit_form": "./js/cytometry/forms/index.js",
            },
            dependencies={},
            devDependencies={},
            aliases={
                "@js/cytometry": "./js/cytometry"
            },
        )
    },
)
