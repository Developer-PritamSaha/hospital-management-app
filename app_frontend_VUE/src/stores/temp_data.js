import { defineStore } from 'pinia'

export const useGlobalTemp = defineStore('temp_data', {
  state: () => ({
    data: {}
  }),

  actions: {
    set(key, value) {
      this.data[key] = value
    },

    get(key) {
      return this.data[key] ?? null
    },

    reset(key) {
      delete this.data[key]
    },

    resetAll() {
      this.data = {}
    }
  }
})