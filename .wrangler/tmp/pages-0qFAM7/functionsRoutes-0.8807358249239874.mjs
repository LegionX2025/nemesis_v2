import { onRequest as __api___catchall___js_onRequest } from "C:\\Users\\LEGIONX\\Downloads\\nemesis\\tracer_scripts\\functions\\api\\[[catchall]].js"

export const routes = [
    {
      routePath: "/api/:catchall*",
      mountPath: "/api",
      method: "",
      middlewares: [],
      modules: [__api___catchall___js_onRequest],
    },
  ]