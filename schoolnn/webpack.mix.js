let mix = require('laravel-mix');
require('laravel-mix-purgecss');

mix.setPublicPath("public")
    .postCss("resources/css/tailwind.css", "public/css/app.css", [
        require("tailwindcss"),
        require('postcss-nested'),
    ]);


if (mix.inProduction()) {
   mix.version();
   mix.purgeCss({
       enabled: true,
       whitelist: [],
       whitelistPatterns: [],
   });
}
