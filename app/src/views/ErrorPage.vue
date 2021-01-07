<!--prettier-ignore-->
<template>
  <a-empty :description="description" />
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  computed: {
    description() {
      const err = this.$route.params;
      return err.status ? `${err.status} ${err.msg}` : '504 Gateway Timeout';
    },
  },
  created() {
    document.title = this.description;
  },
});
</script>

<style lang="scss" scoped>
.ant-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  font-size: 1.5em;
  line-height: 2em;
  transform: translate(-50%, -50%);

  > .ant-empty-image {
    height: 160px;
  }
}
</style>
