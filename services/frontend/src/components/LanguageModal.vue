<script setup lang="ts">
import type { Language } from '@/types/Language';
import { defineProps } from 'vue';
import { LANGUAGES } from '@/utils/constants'

const props = defineProps<{
  onChoose: (language: Language) => void
}>();
</script>

<template>
  <div class="fixed top-0 left-0 right-0 bottom-0">
    <div class="absolute top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50"></div>
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded-lg shadow-lg w-[90%] max-w-[400px]">
      <div class="text-gray-700">
        <div class="mb-1 text-3xl">Select your language</div>
        <div class="mb-1 text-md">Seleccione su idioma | Selecione seu idioma</div>
        <div class="mb-1 text-md"></div>
      </div>
      <hr/>
      <div v-for="lang in $i18n.availableLocales" :key="lang" class="flex items-center justify-between p-2 mt-4 bg-gray-100 rounded-lg cursor-pointer" @click="props.onChoose(lang as Language)">
        <div>{{ LANGUAGES[lang as Language] }}</div>
        <div class="text-xs text-gray-500 ml-2">{{ $t("choose") }}</div>
      </div>
    </div>
  </div>
</template>
