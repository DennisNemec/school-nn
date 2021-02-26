<template>
  <div>
    <Accordion>
      <template v-slot:accordion-preview>
        <div class="flex w-full justify-between">
          <div class="flex items-center w-5/6 text-primary font-bold">
            <div>
              <h3>{{title}}</h3>
            </div>
          </div>

          <div class="w-48 flex justify-end h-10 pr-8 text-white">
            <div class="w-full p-2 pl-6 pr-6 rounded-2xl text-center" v-bind:class="statusColor">
              <p>{{statusText}}</p>
            </div>
          </div>
        </div>
      </template>

      <template v-slot:accordion-content>
        <table class="table-fixed w-1/3 text-primary">
          <tbody>
            <tr>
              <td class="font-bold">Erstellt am</td>
              <td>{{creationDate}}</td>
            </tr>

            <tr>
              <td class="font-bold">Anzahl Bilder</td>
              <td>{{amountOfPictures}}</td>
            </tr>

            <tr>
              <td class="font-bold">Anzahl Kategorien</td>
              <td>{{amountOfCategories}}</td>
            </tr>

            <tr>
              <td class="font-bold">Unklassifizierte Bilder</td>
              <td>{{unlabeledCount}}</td>
            </tr>
          </tbody>
        </table>

        <a class="text-accent" :href="'/datasets/' + id">Details anzeigen</a>

        <div class="mt-10 w-full text-primary">
          <div class="w-full mb-8" v-for="cat in categories" v-bind:key="cat.name">
            <p class="font-bold">{{cat.name}}</p>

            <div class="flex">
              <img loading=lazy v-for="image_id in cat.image_ids" v-bind:key="image_id" :src="baseImagePath + image_id" width="80" height="80">
            </div>
          </div>
        </div>
      </template>
    </Accordion>
  </div>
</template>

<script>
import Accordion from "@/components/Accordion";

export default {
  name: "DatasetAccordion",
  components: {Accordion},

  props: {
    title: String,
    amountOfPictures: String,
    amountOfCategories: String,
    unlabeledCount: Number,
    statusText: String,
    creationDate: String,
    id: Number,
    categories: Array
  },

  data() {
    return {
      baseImagePath: "/images/"
    }
  },

  computed: {
    statusColor() {
      let color = ""

      if (this.unlabeledCount === 0) {
        color = "bg-green"
      } else {
        color = "bg-yellow"
      }

      return color
    }
  }
}
</script>

<style scoped>

</style>