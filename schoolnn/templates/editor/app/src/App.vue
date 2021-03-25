<template>
  <div id="app" class="text-primary font-sans">
    <div class="w-full card">
      <div v-if="invalidState == true" class="w-full p-4 rounded text-white bg-red" >
        <p>{{ errorMessage }}</p>
      </div>
      <div class="p-4 flex items-start flex-wrap">
        <!-- Print preview layer -->
        <div class="w-1/4 self-stretch pt-6 border-text-gray border-dotted border-r-2">
          <h3 class="mb-4">Verfügbare Schichten</h3>
          <draggable
              v-model="providedLayerList"
              class="space-y-4"
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
        <div class="w-2/4 py-6 pl-16">
          <h3 class="mb-4">Ausgewählte Schichten</h3>
          <draggable
              v-model="selectedLayerList"
              class="space-y-4"
              group="layer"
              @start="drag=false"
              @end="drag=true"
              @sort="onArchitectureChange"
              :move="onMove">

            <div class="flex" v-for="element in selectedLayerList" :key="element.id">
              <layer-node v-bind:selected-layer-id="selectedLayer.id" v-on:on-layer-select="onLayerSelect" v-on:on-duplicate-layer="onDuplicateLayer" v-on:on-delete-layer="onDeleteLayer" :layer=element />
            </div>
          </draggable>
        </div>

        <!-- Print configuration -->
        <div class="w-1/4 mb-6 pt-16">
          <layer-configuration v-on:set-invalid-state="onInvalidStateToggle" v-on:on-save="onSave" v-bind:invalid-state="invalidState" v-bind:layer="selectedLayer" />
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

      errorMessage: "",

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

        Initialized by Django
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
    let importData = JSON.parse(document.getElementsByName("architecture_json")[0].value)
    const length = importData.length

    importData.push({
      type: "Dense",
      name: "Output Layer (automatisch generiert)",
      activation: "softmax",
      units: document.getElementsByName("output_dimension")[0].value
    })

    this.selectedLayerList = importData.map((backendLayer, index) => {
      const frontendLayer = {
        id: index,
        first: index === 0,
        last: index === length - 1,
        fixed: index === 0 || index === length - 1,
        note: '',
        name: backendLayer.name,
        layer_information: this.getLayerInformationByType(backendLayer.type),
        layer: {
          type: backendLayer.type,
          properties: []
        },
      }

      return Object.keys(backendLayer).reduce((frontendLayer, key) => {
        frontendLayer.layer.properties.push({
          name: key,
          value: backendLayer[key]
        })

        return frontendLayer
      }, frontendLayer)
    })

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
      if (relatedContext.element.first) {
        return 1
      }

      // make sure items are inserted above the last element
      if (relatedContext.element.last) {
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

      const layerInformation = this.getLayerInformationByType(event.type)

      const newSelectedLayer =  {id: newId, name: event.default_name, layer_information: layerInformation, note: "", layer: layer}

      if (!this.invalidState) {
        this.setSelectedLayer(newSelectedLayer)
      }

      return newSelectedLayer
    },

    // Validate the given architecture
    onArchitectureChange() {
      const isValid = this.isArchitectureValid()

      if (!isValid) {
        this.invalidState = true
      } else {
        this.invalidState = false
        this.setErrorMessage("")
      }
    },

    onInvalidStateToggle(state) {
      this.invalidState = state
    },

    onLayerSelect(layer) {
      if (this.invalidState === true) {
        return
      }

      console.log(layer)

      this.invalidState = false
      this.setSelectedLayer(layer)
    },

    onSave() {
      let layerList = []
      this.selectedLayerList.pop() // remove dummy output layer

      for (const selected_layer of this.selectedLayerList) {
        const selected_layer_dto = {
          type: selected_layer.layer.type,
          name: selected_layer.name
        }

        for (const property of selected_layer.layer.properties) {
          selected_layer_dto[property.name] = property.value
        }

        layerList.push(selected_layer_dto)
      }

      console.log(layerList, this.selectedLayerList)

      document.getElementsByName("architecture_json")[0].value =
          JSON.stringify(layerList,null,2)

      document.querySelector("#architecture_form").submit()
    },

    onDeleteLayer(layer) {
      if (!layer.fixed) {
        this.selectedLayer = this.selectedLayerList[0] // select input layer
        const ind = this.selectedLayerList.indexOf(this.selectedLayerList.find(element => element.id === layer.id))
        this.$delete(this.selectedLayerList, ind)
        this.invalidState = false
        this.onArchitectureChange()
      }
    },

    onDuplicateLayer(layer) {
      // abort if layer is either input- or output-layer
      if (layer.fixed) {
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

      this.onArchitectureChange()
    },

    /* Helper methods */
    setSelectedLayer(layer) {
      this.selectedLayer = layer
    },

    setErrorMessage(message) {
      this.errorMessage = message
    },

    getLayerInformationByType(type) {
      return this.providedLayerList.find(element => element.type === type)
    },

    getNextLayer(currentLayer) {
      const indexOfCurrentLayer = this.selectedLayerList.indexOf(currentLayer)

      if (indexOfCurrentLayer >= 0 && indexOfCurrentLayer < this.selectedLayerList.length - 1) {
        return this.selectedLayerList[indexOfCurrentLayer + 1]
      }

      return false
    },

    isLastLayer(currentLayer) {
      const indexOfCurrentLayer = this.selectedLayerList.indexOf(currentLayer)

      return (indexOfCurrentLayer === this.selectedLayerList.length - 1) ? true : false
    },

    isArchitectureValid() {
      const inputLayer = this.selectedLayerList[0]
      const followingLayer = this.getNextLayer(inputLayer)

      return this.validateAdjacentLayerDimension(inputLayer, null, followingLayer)
    },

    // DFS-like dimension validation
    validateAdjacentLayerDimension(currentLayer, previousOutputDimension, followingLayer) {
      if (this.isLastLayer(currentLayer)) {
        return true
      }

      const currentLayerInformation = this.getLayerInformationByType(currentLayer.layer.type)
      const followingLayerInformation = this.getLayerInformationByType(followingLayer.layer.type)
      const nextLayer = this.getNextLayer(followingLayer)

      if (typeof followingLayerInformation.input_dimension === 'undefined' && typeof currentLayerInformation.output_dimension !== 'undefined') {
        return this.validateAdjacentLayerDimension(followingLayer, currentLayerInformation.output_dimension, nextLayer)
      }

      if (typeof followingLayerInformation.input_dimension === 'undefined' && typeof currentLayerInformation.output_dimension === 'undefined') {
        return this.validateAdjacentLayerDimension(followingLayer, previousOutputDimension, nextLayer)
      }

      if (typeof currentLayerInformation.output_dimension === 'undefined') {
        if (previousOutputDimension !== followingLayerInformation.input_dimension) {
          this.setErrorMessage("Dimension von " + followingLayer.name + " und der vorherigen Schicht stimmen nicht überein.")
          return false
        } else {
          return this.validateAdjacentLayerDimension(followingLayer, previousOutputDimension, nextLayer)
        }
      }

      if (currentLayerInformation.output_dimension === followingLayerInformation.input_dimension) {
        return this.validateAdjacentLayerDimension(followingLayer, currentLayerInformation.output_dimension, nextLayer)
      } else {
        this.setErrorMessage("Dimension von " + followingLayer.name + " und der vorherigen Schicht stimmen nicht überein.")
        return false
      }

    }
  
  },
}

</script>