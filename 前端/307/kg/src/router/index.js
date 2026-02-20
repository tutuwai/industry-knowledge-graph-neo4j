import {createRouter,createWebHashHistory} from "vue-router"
import GraphPage from "../views/GraphPage.vue" //2.引入路由组件,先创建两个界面路由组件
import MapPage from "../views/MapPage.vue"
import MainPage from "../views/MainPage.vue"
import ProfilePage from "../views/ProfilePage.vue"
import PathPage from "../views/PathPage.vue"
import DynamicPage from "../views/DynamicPage.vue"
import PatentDetailPage from "../views/PatentDetailPage.vue"
import CommunityGraphPage from "../views/CommunityGraphPage.vue"

//1.使用模块化，即main中use(router)
//3.将路由与组件映射
//定义一些路由,每个路由都需要映射到一个组件。
const routes = [
    //主路由
    {
      path: '/',
      component: MainPage,
      redirect: '/graph',//重定向，当路径为/时，定向到graph
      children:[
          //子路由
          { path: 'graph', component: GraphPage },//专利信息全景展示
          { path: 'dynamic', component: DynamicPage },//动态演化
          { path: 'map', component: MapPage },//地图分布
          { path: 'profile', component: ProfilePage },//专利画像
          { path: 'path', component: PathPage },//路径分析
          { path: 'patent/:publicationNumber', component: PatentDetailPage }, // 添加专利详情页面的路由
          { path: 'patent/community/:publicationNumber', component: CommunityGraphPage, name: 'CommunityGraph' }, // 添加专利社群图页面的路由
      ]
    },
];
//4.创建router实例并传递 `routes` 配置
// 你可以在这里输入更多的配置，但我们在这里暂时保持简单
const router = createRouter({
  history: createWebHashHistory(),
  routes, // `routes: routes` 的缩写
});
//5.挂载到根实例
export default router; //实例对外暴露