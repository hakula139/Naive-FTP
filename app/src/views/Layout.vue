<template>
  <a-layout id="layout">
    <a-layout-header id="layout-header">
      <router-link
        :to="{ name: 'Layout' }"
        class="title"
      >
        {{ title }}
      </router-link>
    </a-layout-header>
    <a-layout-content id="layout-content">
      <a-breadcrumb :routes="routes">
        <template #separator>
          <span class="path-separator">
            <RightOutlined />
          </span>
        </template>
        <template #itemRender="{ route }">
          <router-link :to="route.path">
            {{ route.breadcrumbName }}
          </router-link>
        </template>
      </a-breadcrumb>
      <file-list :data="fileList" />
    </a-layout-content>
    <a-layout-footer id="layout-footer">
      {{ title }} created by
      <a
        :href="links.blog"
        target="_blank"
      >
        {{ author }}
      </a>
    </a-layout-footer>
  </a-layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import { Route } from 'ant-design-vue/lib/breadcrumb/Breadcrumb';
import { RightOutlined } from '@ant-design/icons-vue';

import { FileList } from '@/components';
import { FileType } from '@/components/types';
import { fileClient } from '@/apis/mocks';

export default defineComponent({
  components: {
    RightOutlined,
    FileList,
  },
  data() {
    return {
      title: 'Naive-FTP',
      author: 'Hakula',
      links: {
        blog: 'https://hakula.xyz',
        repo: 'https://github.com/hakula139/Naive-FTP',
      },
      fileList: [] as FileType[],
    };
  },
  computed: {
    routes() {
      const re = /^\/?|\/?$/g;
      const parts: string[] = this.$route.path.replaceAll(re, '').split('/');
      const breadcrumbs: Route[] = [];
      parts.forEach((part, i) => {
        const parentPath = i ? breadcrumbs[i - 1].path : '/';
        breadcrumbs.push({
          breadcrumbName: decodeURIComponent(part),
          path: `${parentPath}${part}/`,
        });
      });
      return breadcrumbs;
    },
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      const re = /^\/?files\/?/;
      const path: string = this.$route.path.replace(re, '');
      fileClient
        .getFileList({ path })
        .then((resp) => {
          this.fileList = resp.data;
        })
        .catch(() => {
          this.$router.push('NotFound');
        });
    },
  },
});
</script>

<style lang="scss" scoped>
#layout {
  min-height: 100vh;
}

#layout-header {
  position: fixed;
  z-index: 1;
  width: 100%;
  height: 64px;
  background-color: #c41d7f;
  // background-color: #780650;

  > .title {
    float: left;
    color: #e6fffb;
    font-size: 2em;
  }
}

#layout-content {
  margin-top: 64px;
  padding: 0 50px;

  .ant-breadcrumb {
    margin: 20px 0;

    a {
      font-size: 1.5em;
    }

    > span:last-child a {
      font-weight: bolder;
    }

    .path-separator {
      margin: 0 4px;
    }
  }
}

#layout-footer {
  text-align: center;
  font-size: 16px;
}
</style>
