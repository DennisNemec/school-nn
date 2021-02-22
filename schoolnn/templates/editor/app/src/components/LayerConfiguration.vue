<template>
  <div>
    <h1 class="text-lg font-bold">Konfiguration</h1>
    <br />
    <p class="text-icon-gray font-light mb-2">Titel</p>
    <input type="text" class="w-2/3 bg-light-gray font-black p-3 rounded-md" :name=layer.name @change="onChangeName" :value=layer.name  />
    <br /><br/>

    <p class="text-icon-gray font-light mb-2">Typ</p>
    <input type="text" class="w-2/3 bg-light-gray font-black p-3 rounded-md" :value=layer.layer_information.type disabled />
    <br /><br/>

    <!-- print activated properties -->
    <div v-for="property in layer.layer_information.properties.filter(property => property.activated === true)" :key="property.name">
        <p class="text-icon-gray font-light mb-2">{{property.description}}<br/></p>

        <!-- print scalar values -->
        <div v-if="property.value.type === 'scalar'" >
          <input v-if="typeof property.value.step !== 'undefined'" type="number" class="w-2/3 bg-light-gray font-black p-3 rounded-md" :name=property.name :min=property.value.min :max=property.value.max @change="onChangeProperty(property.name, $event)" :value=getPropertyValue(property.name) :step=property.value.step  />
          <input v-else type="number" class="w-2/3 bg-light-gray font-black p-3 rounded-md" :name=property.name :min=property.value.min :max=property.value.max @change="onChangeProperty(property.name, $event)" :value=getPropertyValue(property.name)  />
        </div>

        <!-- print list values -->
        <div v-if="property.value.type === 'list'" >
          <select class="w-2/3 bg-light-gray font-black p-3 rounded-md" :name=property.name @change="onChangeProperty(property.name, $event)">
            <option v-for="selectable_property in property.value.possible_values" :key="selectable_property">
              {{selectable_property}}
            </option>
          </select>

          <br />
        </div>

        <!--- print vector -->
        <div v-if="property.value.type === 'vector'" >
          <input class="w-2/3 bg-light-gray font-black p-3 rounded-md" type="text" :min=property.value.min :max=property.value.max :name=property.name @change="onChangePropertyVector(property.name, $event)" :value=getPropertyValueVector(property.name)  />
        </div>

        <br />
      </div>

    <button v-on:click="$emit('on-save')" class="button-standard disabled:opacity-0" :disabled="invalidState === true">Speichern</button>
  </div>
</template>

<script>
export default {
  name: "LayerConfiguration",
  props: {
    layer: Object,
    invalidState: Boolean
  },

  data() {
    return {
      borderClass: "border-2",
      borderRedClass: "border-red-500",
      currentSelectedElement: {},
    }
  },

  watch: {
    invalidState(newState, oldState) {
      if (oldState === true && newState === false) {
        this.removeColorBorderError(this.currentSelectedElement)
      }

      if (oldState === false && newState === true) {
        this.addColorBorderError(this.currentSelectedElement)
      }
    }
  },

  methods: {
    isInRange(value, min, max) {
      return value > min && value < max
    },

    addColorBorderError(htmlElement) {
      htmlElement.classList.add(this.borderClass)
      htmlElement.classList.add(this.borderRedClass)
    },

    removeColorBorderError(htmlElement) {
      if (htmlElement.classList.contains(this.borderClass) && htmlElement.classList.contains(this.borderRedClass)) {
        htmlElement.classList.remove(this.borderClass)
        htmlElement.classList.remove(this.borderRedClass)
      }
    },

    validateInput(htmlElement, min, max, value) {
      let isValid = true

      if (!this.isInRange(value, min, max)) {
        isValid = false
      }

      this.$emit("set-invalid-state", !isValid)

      return isValid
    },

    getPropertyValue(propertyName) {
      return this.layer.layer.properties.find(element => element.name === propertyName).value
    },

    getPropertyValueVector(propertyName) {
      return this.layer.layer.properties.find(element => element.name === propertyName).value.join("x")
    },

    onChangeProperty(propertyName, event) {
      const value = event.target.value
      const min = event.target.min
      const max = event.target.max
      this.currentSelectedElement = event.target

      if (typeof min !== 'undefined' && typeof max !== 'undefined') {
        this.validateInput(event.target, min, max, value)
      }

      this.layer.layer.properties.find(element => element.name === propertyName).value = event.target.value
    },


    onChangePropertyVector(propertyName, event) {
      const delimiter = "x"
      const value = event.target.value.split(delimiter).map(x => parseInt(x))
      const min = event.target.min
      const max = event.target.max
      this.currentSelectedElement = event.target
      let isValid = true

      // check if values are valid
      for (let val of value) {
        if (!this.isInRange(val, min, max)) {
          isValid = false
        }
      }

      this.$emit('set-invalid-state', !isValid)

      this.layer.layer.properties.find(element => element.name === propertyName).value = value

    },

    onChangeName(event) {
      this.layer.name = event.target.value
    }
  }
}
</script>