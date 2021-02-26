<template>
  <div class="
    flex
    items-center
    text-center
    card
    w-5/6
    hover:border-icon-gray
    border-2
    border-light-gray
    pl-2
    cursor-move
    "
  >
    <span>
      <svg class="fill-current text-icon-gray" width="27" height="27" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" >
        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
      </svg>
    </span>

    <h4 class="select-none ml-3">
      {{title}}
    </h4>
  </div>
</template>

<script>
export default {
  name: "LayerPreview",
  props: [
      "title"
  ],
}
</script>

<style scoped>

</style>