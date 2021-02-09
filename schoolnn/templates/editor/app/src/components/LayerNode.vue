<template>
  <div class="flex shadow-md text-center bg-white mb-5 w-5/6 rounded-md hover:border-primary border-2 p-4" v-if="typeof layer !== 'undefined'" v-bind:class="(selectedLayerId === layer.id) ? 'border-primary' : 'border-white'">
    <span v-on:click="$emit('on-layer-select', layer)">
      <svg class="fill-current text-icon-gray" width="27" height="27" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" >
        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
      </svg>
    </span>

    <div class="text-left select-none w-full">
      <div v-on:click="$emit('on-layer-select', layer)">
        <p class="font-bold">{{layer.name}}</p>
        <p>Typ: {{layer.layer_information.type}}</p>
        <p v-for="property in layer.layer_information.properties" :key="property.name">
          {{property.description}}: {{
            Array.isArray(getProperty(property.name).value)
                ? getProperty(property.name).value.join("x")
                : getProperty(property.name).value
          }}
        </p>
      </div>

      <div class="inline-flex space-x-2 text-icon-gray">
        <a class="flex-1 cursor-pointer" v-on:click="$emit('on-delete-layer', layer)">Löschen</a>
        <svg class="inline self-center text-icon-gray fill-current"  width="5" height="5" viewBox="0 0 120 120" version="1.1"
             xmlns="http://www.w3.org/2000/svg">
          <circle cx="60" cy="60" r="50"/>
        </svg>
        <div class="flex-1 cursor-pointer" v-on:click="$emit('on-duplicate-layer', layer)">Duplizieren</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LayerNode",

  props: {
    layer: Object,
    selectedLayerId: Number
  },

  methods: {
    getProperty(key) {
      return this.layer.layer.properties.find(element => element.name === key)
    }
  }
}
</script>