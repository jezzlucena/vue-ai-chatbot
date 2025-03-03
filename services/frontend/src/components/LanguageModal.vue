<script setup lang="ts">
import { LANGUAGES } from '@/utils/constants'
import type { Language } from '@/types/Language'

defineProps<{
  onChoose: (language: Language) => void,
  onClose: () => void
}>()
</script>

<template>
  <div class="fixed top-0 left-0 right-0 bottom-0">
    <div
      class="absolute top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50"
      @click="onClose"
    ></div>
    <div
      class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded-lg shadow-lg w-[90%] max-w-[400px]"
    >
      <div class="text-gray-700">
        <div class="flex text-2xl">
          <div class="mb-1 grow">
            {{ $t('selectLanguage', 1, { locale: 'en_US' }) }}
          </div>

          <div class="ml-2 cursor-pointer" @click="onClose">&times;</div>
        </div>
        <div class="mb-2 text-md">
          {{ $t('selectLanguage', 1, { locale: 'es_ES' }) }}
          {{ ' | ' }}
          {{ $t('selectLanguage', 1, { locale: 'pt_BR' }) }}
        </div>
      </div>
      <hr />
      <div class="mt-2 text-sm">
        <div
          v-for="language in $i18n.availableLocales"
          :key="language"
          class="flex items-center justify-between p-2 mt-2 bg-gray-100 rounded-lg cursor-pointer"
          :class="{ 'bg-gray-300': $i18n.locale === language}"
          @click="onChoose(language as Language)"
        >
          <div>{{ LANGUAGES[language as Language].long }}</div>
          <div class="text-xs text-gray-500 ml-2">{{ $t('choose') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
