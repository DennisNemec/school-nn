<template>
  <div id="app" class="text-primary font-sans">
    <div class="flex flex-wrap overflow-hidden bg-light-gray h-screen-minus-header w-full float-right">

      <!-- Print preview layer -->
      <div class="w-1/6 pt-5 overflow-hidden border-gray-300 border-dashed border-r-2 pl-5">
        <h1 class="text-lg font-bold">Verfügbare Schichten</h1>
        <br />
        <draggable
            v-model="providedLayerList"
            :group="{ name: 'layer', pull: 'clone', put: false }"
            @start="drag=true"
            @end="drag=true"
            :move="onMove"
            :clone="onClone"
        >

          <div class="flex" v-for="element in providedLayerList" :key="element.type">
            <layer-preview :title=element.default_name />
          </div>
        </draggable>

      </div>

      <!-- Print selected Layer Draggable-List -->
      <div class="w-3/6 pb-28 pt-5 h-screen overflow-y-scroll pl-10">
        <h1 class="text-lg font-bold">Ausgewählte Schichten</h1>
        <br/>
        <draggable
            v-model="selectedLayerList"
            group="layer"
            @start="drag=false"
            @end="drag=true"
            :move="onMove">

          <div class="flex" v-for="element in selectedLayerList" :key="element.id">
            <layer-node v-bind:selected-layer-id="selectedLayer.id" v-on:on-layer-select="onLayerSelect" v-on:on-duplicate-layer="onDuplicateLayer" v-on:on-delete-layer="onDeleteLayer" :layer=element />
          </div>
        </draggable>
      </div>

      <!-- Print configuration -->
      <div class="w-2/6 overflow-hidden pt-5 pl-10 bg-white">
        <div class="flex flex-wrap overflow-hidden relative h-screen">

          <div class="w-full min-h-full overflow-hidden flex-grow">
            <layer-configuration v-on:set-invalid-state="onInvalidStateToggle" v-on:on-save="onSave" v-bind:invalid-state="invalidState" v-bind:layer="selectedLayer" />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>

import draggable from 'vuedraggable'
import _ from 'lodash'

export default {
  name: 'App',
  components: {
    draggable
  },

  data() {
    return {
      /*
        Current selected layer
       */
      selectedLayer: {},

      invalidState: false,

      /*
        Id counter. Is being implemented if a preview layer has been dragged to the selected layer field.

        Initially set to 2 due to always existing input and output layer
       */
      idCursor: 2,

      /*
        Provided layer-list

        Given by Django
       */
      providedLayerList: [],

      /*
        Layers on the drag and drop field
        Input and output layer are obligatory

        Given by Django
       */
      selectedLayerList: [],
    }
  },

  /*
    Constructor
  */
  created() {
    // use data given by Django
    this.providedLayerList = JSON.parse(document.getElementsByName("django_provided_layer_list")[0].value)
    this.selectedLayerList = JSON.parse(document.getElementsByName("architecture_json")[0].value)

    // set initial selected layer to the input layer
    this.selectedLayer = this.selectedLayerList.find(element => element.id === 1)
  },

  methods: {
    /* Events */

    onMove({draggedContext, relatedContext}) {
      // return false means the drag is being aborted
      // required especially for fixed items
      if (typeof draggedContext.element.fixed != 'undefined' && draggedContext.element.fixed === true) {
        return false
      }

      // make sure items are not inserted above the first element
      if (typeof relatedContext.element.first != 'undefined') {
        return 1
      }

      // make sure items are inserted above the last element
      if (typeof relatedContext.element.last != 'undefined') {
        return -1
      }
    },

    onClone(event) {
      this.idCursor += 1
      const newId = this.idCursor

      // extract only property name and default_value
      let properties = []
      for (let property of event.properties) {
        const propertyObject = {
          name: property.name,
          value: property.value.default_value
        }

        properties.push(propertyObject)
      }

      const layer = {
        type: event.type,
        properties: properties
      }

      const layerInformation = this.providedLayerList.find(element => element.type === event.type)

      const newSelectedLayer =  {id: newId, name: event.default_name, layer_information: layerInformation, note: "", layer: layer}

      if (!this.invalidState) {
        this.setSelectedLayer(newSelectedLayer)
      }

      return newSelectedLayer
    },


    onInvalidStateToggle(state) {
      this.invalidState = state
    },

    onLayerSelect(layer) {
      if (this.invalidState === true) {
        return
      }

      this.invalidState = false
      this.setSelectedLayer(layer)
    },

    onSave() {
      document.getElementsByName("architecture_json")[0].value =
          JSON.stringify(this.selectedLayerList,null,2)

      document.querySelector("#architecture_form").submit()
    },

    onDeleteLayer(layer) {
      if (layer.id > 2) {
        this.selectedLayer = this.selectedLayerList.find(element => element.id === 1)
        const ind = this.selectedLayerList.indexOf(this.selectedLayerList.find(element => element.id === layer.id))
        this.$delete(this.selectedLayerList, ind)
        this.invalidState = false
      }
    },

    onDuplicateLayer(layer) {
      // abort if layer is either input- or output-layer
      if (layer.id < 3) {
        return
      }

      // clone layer
      let clonedLayer = _.clone(layer)
      this.idCursor += 1
      let newId = this.idCursor
      clonedLayer.id = newId

      // get old index
      let oldIndex = this.selectedLayerList.indexOf(layer)

      // add
      this.selectedLayerList.splice(oldIndex, 0, clonedLayer)
    },

    /* Helper methods */
    setSelectedLayer(layer) {
      this.selectedLayer = layer
    },
  },
}

</script>