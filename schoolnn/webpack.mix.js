let mix = require('laravel-mix');
require('laravel-mix-purgecss');

mix.setPublicPath("public")
    .postCss("resources/css/tailwind.css", "public/css/app.css", [
        require("tailwindcss"),
        require('postcss-nested'),
    ]);
    //.js('resources/js/app.js', 'public/js/app.js').vue();


if (mix.inProduction()) {
   mix.version();
   mix.purgeCss({
       enabled: true,
       whitelist: [],
       whitelistPatterns: [],
   });
}
