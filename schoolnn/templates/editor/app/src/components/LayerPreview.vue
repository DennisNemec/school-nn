<template>
  <div class="
    flex
    items-center
    shadow-md
    text-center
    primary
    bg-white
    mb-5 h-20
    w-5/6
    rounded-md
    hover:border-black
    border-2
    border-white
    pl-2
    "
  >
    <span>
      <svg class="fill-current text-icon-gray" width="27" height="27" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" >
        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
      </svg>
    </span>

    <p class="font-bold select-none">
      {{title}}
    </p>
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