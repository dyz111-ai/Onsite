import { Chart, registerables } from 'chart.js'

// 注册 Chart.js 所有组件
Chart.register(...registerables)

// 解析训练日志
export function parseTrainingLog(logContent) {
  try {
    const epochLines = logContent.match(/Epoch \[\d+\]\[\d+\/\d+\].*$/gm)
    if (!epochLines || epochLines.length === 0) {
      return null
    }
    
    const stages = []
    
    for (const line of epochLines) {
      const epochMatch = line.match(/Epoch \[(\d+)\]\[(\d+)\/(\d+)\]/)
      const epoch = epochMatch ? parseInt(epochMatch[1]) : 0
      const step = epochMatch ? parseInt(epochMatch[2]) : 0
      const totalSteps = epochMatch ? parseInt(epochMatch[3]) : 0
      
      const etaMatch = line.match(/eta:\s*([^,]+)/)
      const eta = etaMatch ? etaMatch[1].trim() : 'N/A'
      
      const lrMatch = line.match(/lr:\s*([\d.e-]+)/)
      const lr = lrMatch ? lrMatch[1] : 'N/A'
      
      const timeMatch = line.match(/time:\s*([\d.]+)/)
      const time = timeMatch ? timeMatch[1] : 'N/A'
      
      const dataTimeMatch = line.match(/data_time:\s*([\d.]+)/)
      const dataTime = dataTimeMatch ? dataTimeMatch[1] : 'N/A'
      
      const memoryMatch = line.match(/memory:\s*([\d.]+)/)
      const memory = memoryMatch ? memoryMatch[1] : 'N/A'
      
      const trackLosses = {
        frame_0: { cls: [], bbox: [], past_trajs: [] },
        frame_1: { cls: [], bbox: [], past_trajs: [] },
        frame_2: { cls: [], bbox: [], past_trajs: [] }
      }
      
      const mapLosses = {
        main: {},
        d0: {},
        d1: {},
        d2: {}
      }
      
      const otherLosses = {
        motion: {},
        occ: {},
        planning: {},
        uncategorized: {}
      }
      
      const lossMatches = line.matchAll(/([\w.]+):\s*([\d.]+)/g)
      for (const match of lossMatches) {
        const key = match[1]
        const value = parseFloat(match[2]).toFixed(4)
        
        if (key.startsWith('track.frame_')) {
          const frameMatch = key.match(/track\.frame_(\d+)_loss_(cls|bbox|past_trajs)_(\d+)/)
          if (frameMatch) {
            const frameNum = frameMatch[1]
            const lossType = frameMatch[2]
            const layer = frameMatch[3]
            trackLosses[`frame_${frameNum}`][lossType].push({ layer, value })
          }
        } else if (key.startsWith('map.')) {
          const parts = key.split('.')
          if (parts.length === 2) {
            mapLosses.main[parts[1]] = value
          } else if (parts.length === 3) {
            const subKey = parts[1]
            const lossName = parts[2]
            if (!mapLosses[subKey]) mapLosses[subKey] = {}
            mapLosses[subKey][lossName] = value
          }
        } else if (key.startsWith('motion.')) {
          otherLosses.motion[key] = value
        } else if (key.startsWith('occ.') || key.startsWith('occupancy.')) {
          otherLosses.occ[key] = value
        } else if (key.startsWith('planning.') || key.startsWith('plan.')) {
          otherLosses.planning[key] = value
        } else if (key.includes('.') || key.includes('_')) {
          otherLosses.uncategorized[key] = value
        }
      }
      
      stages.push({
        epoch,
        step,
        totalSteps,
        eta,
        lr,
        time,
        dataTime,
        memory,
        trackLosses,
        mapLosses,
        otherLosses
      })
    }
    
    return { stages }
  } catch (error) {
    console.error('解析训练日志失败:', error)
    return null
  }
}

// 通用图表配置
const chartColors = ['#42b983', '#667eea', '#f093fb', '#f6d365', '#fda085', '#a8edea']

const commonChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { font: { size: 11 } } }
  },
  scales: { y: { beginAtZero: false } }
}

// Track 分类损失 - Frame 0
export function drawTrackClsF0Chart(chartRef, trainingInfo, chartInstance) {
  console.log('drawTrackClsF0Chart called')
  console.log('chartRef:', chartRef)
  console.log('trainingInfo:', trainingInfo)
  
  if (!trainingInfo || !chartRef) {
    console.log('Missing trainingInfo or chartRef')
    return null
  }
  
  if (chartInstance) {
    console.log('Destroying old chart instance')
    chartInstance.destroy()
  }
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_0.cls
    
    console.log('Frame losses:', frameLosses)
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_0.cls[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    console.log('Creating chart with datasets:', datasets.length)
    
    const chart = new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
    
    console.log('Chart created successfully:', chart)
    return chart
  } catch (error) {
    console.error('绘制Track分类损失Frame 0图表失败:', error)
    return null
  }
}

// Track 分类损失 - Frame 1
export function drawTrackClsF1Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_1.cls
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_1.cls[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track分类损失Frame 1图表失败:', error)
    return null
  }
}

// Track 分类损失 - Frame 2
export function drawTrackClsF2Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_2.cls
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_2.cls[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track分类损失Frame 2图表失败:', error)
    return null
  }
}

// Track 边界框损失 - Frame 0
export function drawTrackBboxF0Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_0.bbox
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_0.bbox[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track边界框损失Frame 0图表失败:', error)
    return null
  }
}

// Track 边界框损失 - Frame 1
export function drawTrackBboxF1Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_1.bbox
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_1.bbox[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track边界框损失Frame 1图表失败:', error)
    return null
  }
}

// Track 边界框损失 - Frame 2
export function drawTrackBboxF2Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_2.bbox
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_2.bbox[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track边界框损失Frame 2图表失败:', error)
    return null
  }
}

// Track 轨迹损失 - Frame 0
export function drawTrackTrajF0Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_0.past_trajs
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_0.past_trajs[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track轨迹损失Frame 0图表失败:', error)
    return null
  }
}

// Track 轨迹损失 - Frame 1
export function drawTrackTrajF1Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_1.past_trajs
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_1.past_trajs[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track轨迹损失Frame 1图表失败:', error)
    return null
  }
}

// Track 轨迹损失 - Frame 2
export function drawTrackTrajF2Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const datasets = []
    const frameLosses = stages[0].trackLosses.frame_2.past_trajs
    
    for (let layer = 0; layer < frameLosses.length; layer++) {
      datasets.push({
        label: `Layer ${layer}`,
        data: stages.map(s => parseFloat(s.trackLosses.frame_2.past_trajs[layer]?.value) || 0),
        borderColor: chartColors[layer % chartColors.length],
        backgroundColor: chartColors[layer % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      })
    }
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Track轨迹损失Frame 2图表失败:', error)
    return null
  }
}

// Map 主要损失
export function drawMapMainChart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const mapKeys = Object.keys(stages[0].mapLosses.main)
    const mapDatasets = mapKeys.map((key, index) => {
      return {
        label: key,
        data: stages.map(s => parseFloat(s.mapLosses.main[key]) || 0),
        borderColor: chartColors[index % chartColors.length],
        backgroundColor: chartColors[index % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      }
    })
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets: mapDatasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Map主要损失图表失败:', error)
    return null
  }
}

// Map D0 层损失
export function drawMapD0Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const mapKeys = Object.keys(stages[0].mapLosses.d0)
    const mapDatasets = mapKeys.map((key, index) => {
      return {
        label: key,
        data: stages.map(s => parseFloat(s.mapLosses.d0[key]) || 0),
        borderColor: chartColors[index % chartColors.length],
        backgroundColor: chartColors[index % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      }
    })
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets: mapDatasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Map D0损失图表失败:', error)
    return null
  }
}

// Map D1 层损失
export function drawMapD1Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const mapKeys = Object.keys(stages[0].mapLosses.d1)
    const mapDatasets = mapKeys.map((key, index) => {
      return {
        label: key,
        data: stages.map(s => parseFloat(s.mapLosses.d1[key]) || 0),
        borderColor: chartColors[index % chartColors.length],
        backgroundColor: chartColors[index % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      }
    })
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets: mapDatasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Map D1损失图表失败:', error)
    return null
  }
}

// Map D2 层损失
export function drawMapD2Chart(chartRef, trainingInfo, chartInstance) {
  if (!trainingInfo || !chartRef) return null
  if (chartInstance) chartInstance.destroy()
  
  try {
    const stages = trainingInfo.stages
    const labels = stages.map(s => `E${s.epoch}-S${s.step}`)
    const mapKeys = Object.keys(stages[0].mapLosses.d2)
    const mapDatasets = mapKeys.map((key, index) => {
      return {
        label: key,
        data: stages.map(s => parseFloat(s.mapLosses.d2[key]) || 0),
        borderColor: chartColors[index % chartColors.length],
        backgroundColor: chartColors[index % chartColors.length].replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.4,
        borderWidth: 2
      }
    })
    
    return new Chart(chartRef, {
      type: 'line',
      data: { labels, datasets: mapDatasets },
      options: commonChartOptions
    })
  } catch (error) {
    console.error('绘制Map D2损失图表失败:', error)
    return null
  }
}

// 辅助函数：按Epoch分组stages
export function getEpochGroups(stages) {
  const groups = {}
  stages.forEach((stage, index) => {
    if (!groups[stage.epoch]) {
      groups[stage.epoch] = {
        number: stage.epoch,
        stages: []
      }
    }
    groups[stage.epoch].stages.push({
      index,
      step: stage.step,
      ...stage
    })
  })
  return Object.values(groups)
}
