<template>
  <div id="app" class="w-full space-y-4">
    <div v-if="datasets.length === 0">
      <article class="card">
        <h3>Oh wow!</h3>
        <p class="mt-4">Es wurden noch keine Datensätze angelegt. Klicke oben auf den Button <span class="font-bold">„Datensatz hinzufügen“</span>, um eine neue Architektur anzulegen.</p>
      </article>
    </div>
    <DatasetAccordion v-for="dataset in datasets" v-bind:key="dataset.name" class="card" :id=dataset.id :amount-of-categories=dataset.label_amount :amount-of-pictures=dataset.image_amount :title=dataset.name :creation-date=dataset.created_at :unlabeled-count=dataset.status.is_completely_labeled :status-text=dataset.status.text :categories=dataset.label />
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