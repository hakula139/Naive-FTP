module.exports = {
  css: {
    loaderOptions: {
      less: {
        lessOptions: {
          modifyVars: {
            'primary-color': '#3030FF',
            'link-color': '#FF6600',
            'border-radius-base': '4px',
          },
          javascriptEnabled: true,
        },
      },
    },
  },
}