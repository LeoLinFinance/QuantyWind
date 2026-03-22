interface VolumeSparklineProps {
  data: number[]
  width?: number
  height?: number
}

export default function VolumeSparkline({ data, width = 80, height = 30 }: VolumeSparklineProps) {
  if (!data || data.length === 0) {
    return <div style={{ width, height }} className="bg-gray-100 rounded" />
  }

  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1

  // 生成柱状图路径
  const barWidth = width / data.length
  const padding = 2

  return (
    <svg width={width} height={height} className="inline-block">
      {data.map((value, index) => {
        const barHeight = ((value - min) / range) * (height - 4) + 2
        const x = index * barWidth + padding / 2
        const y = height - barHeight

        return (
          <rect
            key={index}
            x={x}
            y={y}
            width={barWidth - padding}
            height={barHeight}
            fill={index === data.length - 1 ? '#3b82f6' : '#9ca3af'}
            opacity={0.8}
          />
        )
      })}
    </svg>
  )
}
