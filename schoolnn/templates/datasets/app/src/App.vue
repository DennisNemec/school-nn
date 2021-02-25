<template>
  <div id="app" class="w-full">
    <DatasetAccordion v-for="dataset in datasets" v-bind:key="dataset.name" class="bg-white rounded-md p-5 shadow-lg mb-10" :amount-of-categories=dataset.label_amount :amount-of-pictures=dataset.image_amount :title=dataset.name :creation-date=dataset.created_at :unlabeled-count=dataset.status.is_completely_labeled :status-text=dataset.status.text :categories=dataset.label />
  </div>
</template>

<script>
import DatasetAccordion from "@/components/DatasetAccordion";

export default {
  name: 'App',
  components: {DatasetAccordion},

  created() {
    this.datasets = JSON.parse(document.getElementById("django_dataset_list").value)    
  }, 

  data() {
    return {
      datasets: [],
    }
  }
}
</script>