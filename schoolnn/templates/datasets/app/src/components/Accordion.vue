<template>
  <div class="overflow-hidden">
    <!-- Preview -->
    <div class="w-full">
      <div class="flex justify-between">
        <!-- arrow -->
        <div class="text-icon-gray cursor-pointer" @click="onCollapse">
          <svg :class="isCollapsed === true ? 'transform rotate-90' : ''" id="arrow" width="40px" height="40px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 5l7 7-7 7" />
          </svg>
        </div>

        <div class="flex w-full items-center pl-2 cursor-pointer" @click="onCollapse">
          <slot name="accordion-preview"></slot>
        </div>
      </div>

      <!-- Collapsed -->
      <div class="ml-12 mt-5" v-bind:class="collapsed">
        <div class="pt-5">
          <slot name="accordion-content"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Accordion",

  data() {
    return {
      isCollapsed: false
    }
  },

  methods: {
    onCollapse: function() {
      this.isCollapsed = !this.isCollapsed
    }
  },

  computed: {
    collapsed() {
      return this.isCollapsed === false ? 'hidden' : 'visible'
    }
  }
}
</script>