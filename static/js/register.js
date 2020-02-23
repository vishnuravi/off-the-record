window.onload = function () {

  Vue.use(window.vuelidate.default);
  var required = window.validators.required;
  var phone_number = document.getElementById("phone_number").value;

  const app = new Vue({
    el: '#app',
    data: {
      first_name: '',
      last_name: '',
      date_of_birth: '',
      phone_number: phone_number,
      submitted: false, // form submitted
      registered: false, // user registered by API
    },
    methods: {
      registerUser: function (e) {
        
        this.submitted = true;
        this.$v.$touch();
        if (this.$v.$invalid) {
          return;
        }

        var self = this;
        axios.post('/create_user', {
          first_name: self.first_name,
          last_name: self.last_name,
          date_of_birth: self.date_of_birth,
          phone_number: self.phone_number
        })
          .then(function (response) {
            self.registered = true;
            console.log(response);
          })
          .catch(function (error) {
            console.log(error.message);
          });
      }
    },
    validations: {
      first_name: { required },
      last_name: { required },
      date_of_birth: { required },
      phone_number: { required }
    }
  })
}