import { m as mousetrap } from "./mousetrap-ce6b1514.js";
const VueMousetrapPlugin = {
  install(app) {
    app.config.globalProperties.$mousetrap = mousetrap;
  }
};
export {
  VueMousetrapPlugin as V
};
