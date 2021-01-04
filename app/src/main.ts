import { createApp } from 'vue';

import App from './App.vue';
import './registerServiceWorker';
import router from './router';

import { Button, Breadcrumb, Layout, Table } from 'ant-design-vue';

const app = createApp(App);

app.use(router);

// Ant Design
app.use(Button).use(Breadcrumb).use(Layout).use(Table);

app.mount('#app');
