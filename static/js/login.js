var app = Vue.createApp({
  data: function() {
    return {
      validCredentials: {
        username: "lightscope",
        password: "lightscope"
      },
      model: {
        username: "",
        password: ""
      },
      loading: false,
      rules: {
        username: [
          {
            required: true,
            message: "Username is required",
            trigger: "blur"
          },
          {
            min: 4,
            message: "Username length should be at least 5 characters",
            trigger: "blur"
          }
        ],
        password: [
          { required: true, message: "Password is required", trigger: "blur" },
          {
            min: 5,
            message: "Password length should be at least 5 characters",
            trigger: "blur"
          }
        ]
      }
    };
  },
  methods: {
    async login() {
      let this_ = this;
      let valid = await this_.$refs.form.validate();
      if (!valid) {
        return;
      }

      this_.loading = true;
      $.ajax({
        url: '/auth/token',
        type: 'POST',
        data: await this_.model, //this_.$refs.form.model,
        success: function()
        {
          this_.loading = false;
          this_.$message.success("Login successfull");
          window.location.href="/";
        },
        error: function()
        {          
          this_.loading = false;
          this_.$message.error("Username or password is invalid");
        }
      })
    }
  }
});
app.use(ElementPlus).mount("#app");