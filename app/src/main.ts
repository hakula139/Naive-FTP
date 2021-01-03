import { createApp } from 'vue';

import App from './App.vue';
import './registerServiceWorker';
import router from './router';

import { Breadcrumb, Layout } from 'ant-design-vue';

const app = createApp(App);

app.use(router);

// Ant Design
app.use(Breadcrumb).use(Layout);

app.mount('#app');
