window.onload = function () {

  Vue.use(window.vuelidate.default);
  var required = window.validators.required;
  var token = document.getElementById("token").value;
  var phone_number = document.getElementById("phone_number").value;

  const app = new Vue({
    el: '#app',
    data: {
      message: '',
      token: token,
      phone_number: phone_number,
      messageAreaVisible: true,
      processed: false, // form successfully processed by API
      submitted: false, // form submitted
      countdown: 5
    },
    methods: {
      toggleMessageArea: function (e) {
        this.messageAreaVisible = !this.messageAreaVisible;
        e.preventDefault();
      },
      clearMessage: function (e) {
        this.message = '',
          e.preventDefault();
      },
      sendMessage: function (e) {

        this.submitted = true;
        this.$v.$touch();
        if (this.$v.$invalid) {
          return;
        }

        var self = this;
        axios.post('/send', {
          message: self.message,
          token: self.token,
          phone_number: self.phone_number
        })
          .then(function (response) {
            // display the success message
            self.processed = true;

            // start the countdown
            var countdownTimer = setInterval(function () {
              self.countdown--;
              // when countdown ends, delete the app container from the DOM
              if (self.countdown <= 0) {
                var appContainer = document.getElementById('app-container');
                appContainer.style.visibility = "hidden";
                clearInterval(countdownTimer);
              }
            }, 1000)
            console.log(response);
          })
          .catch(function (error) {
            console.log(error);
          });
      }
    },
    validations: {
      message: { required }
    }
  })
}