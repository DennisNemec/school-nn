import Vue from 'vue'
import App from './App.vue'
import "tailwindcss/tailwind.css"

// Custom components
import LayerNode from "@/components/LayerNode";
import LayerPreview from "@/components/LayerPreview";
import LayerConfiguration from "@/components/LayerConfiguration";

Vue.component("layer-node", LayerNode)
Vue.component("layer-preview", LayerPreview)
Vue.component("layer-configuration", LayerConfiguration)

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
