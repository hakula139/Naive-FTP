import { createApp } from 'vue';

import App from './App.vue';
import './registerServiceWorker';
import router from './router';

import { Button } from 'ant-design-vue';

const app = createApp(App);

app.use(router);

// Ant Design
app.use(Button);

app.mount('#app');
