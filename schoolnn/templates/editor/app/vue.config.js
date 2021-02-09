const path = require("path");

module.exports = {
    outputDir: path.resolve(__dirname, "../../../public"),

    configureWebpack: config => {
        config.output.filename = 'js/editor.[name].js'
        config.output.chunkFilename = 'js/editor.[name].js';
    },

    chainWebpack: config => {
        config.plugins.delete('html')
        config.plugins.delete('preload')
        config.plugins.delete('prefetch')
  }
}