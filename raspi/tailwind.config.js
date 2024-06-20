module.exports = {
  content: ["./templates/**/*.html", "./static/src/**/*.js"],
  theme: {
    extend: {
      colors: {
        primary: "#FE6F3A",
        secondary: "#101214",
        grey: "#F2F4F5",
        dark_grey: "#ADB2B4",
      },
      height: {
        112: "28rem",
        128: "32rem",
        144: "36rem",
        160: "40rem",
      },
      margin: {
        112: "28rem",
        128: "32rem",
        144: "36rem",
        160: "40rem",
      },
      fontFamily: {
        roboto: ['"Roboto Mono"', "sans-serif"],
        // Add more custom font families as needed
      },
    },
  },
  plugins: [],
};
