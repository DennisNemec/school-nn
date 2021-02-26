<template>
  <div>
    <Accordion>
      <template v-slot:accordion-preview>
        <div class="flex w-full justify-between">
          <div class="flex items-center w-5/6 text-primary font-bold">
            <div>
              <p>{{title}}</p>
              <p class="font-light text-icon-gray">Erstellt am {{creationDate}}</p>
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
        <table class="table-fixed w-1/3 text-primary mb-4">
          <thead>
            <tr>
              <th class="w-2/5"></th>
              <th class="w-1/2"></th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td>Anzahl Bilder</td>
              <td class="font-bold">{{amountOfPictures}}</td>
            </tr>

            <tr>
              <td>Anzahl Kategorien</td>
              <td class="font-bold">{{amountOfCategories}}</td>
            </tr>

            <tr>
              <td>Unklassifizierte Bilder</td>
              <td class="font-bold">{{unlabeledCount}}</td>
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