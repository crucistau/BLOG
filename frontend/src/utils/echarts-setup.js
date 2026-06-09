// @author beishi
// @date 2026/6/9
// @description ECharts china map geo JSON loader - registers china map for ECharts map charts
import { use } from 'echarts/core'

export async function setupChinaMap() {
  const echarts = await import('echarts/core')
  const chinaJson = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    .then(res => res.json())
  echarts.registerMap('china', chinaJson)
}
