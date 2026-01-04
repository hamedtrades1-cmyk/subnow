'use client'

import { useRef, useState, useCallback, useEffect } from 'react'

interface UseVideoPlayerOptions {
  onTimeUpdate?: (time: number) => void
  onDurationChange?: (duration: number) => void
  onEnded?: () => void
  onLoadedMetadata?: () => void
}

interface UseVideoPlayerReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>
  
  // State
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  isMuted: boolean
  isLoading: boolean
  playbackRate: number
  
  // Controls
  play: () => void
  pause: () => void
  toggle: () => void
  seek: (time: number) => void
  seekRelative: (delta: number) => void
  setVolume: (volume: number) => void
  toggleMute: () => void
  setPlaybackRate: (rate: number) => void
  
  // Frame navigation
  nextFrame: () => void
  prevFrame: () => void
}

export function useVideoPlayer(
  options: UseVideoPlayerOptions = {}
): UseVideoPlayerReturn {
  const { onTimeUpdate, onDurationChange, onEnded, onLoadedMetadata } = options

  const videoRef = useRef<HTMLVideoElement>(null)
  
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolumeState] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [playbackRate, setPlaybackRateState] = useState(1)

  // Play
  const play = useCallback(() => {
    videoRef.current?.play()
  }, [])

  // Pause
  const pause = useCallback(() => {
    videoRef.current?.pause()
  }, [])

  // Toggle play/pause
  const toggle = useCallback(() => {
    if (isPlaying) {
      pause()
    } else {
      play()
    }
  }, [isPlaying, play, pause])

  // Seek to specific time
  const seek = useCallback((time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, Math.min(time, duration))
    }
  }, [duration])

  // Seek relative to current time
  const seekRelative = useCallback((delta: number) => {
    if (videoRef.current) {
      seek(videoRef.current.currentTime + delta)
    }
  }, [seek])

  // Set volume (0-1)
  const setVolume = useCallback((vol: number) => {
    const clampedVol = Math.max(0, Math.min(1, vol))
    if (videoRef.current) {
      videoRef.current.volume = clampedVol
    }
    setVolumeState(clampedVol)
    if (clampedVol > 0) {
      setIsMuted(false)
      if (videoRef.current) {
        videoRef.current.muted = false
      }
    }
  }, [])

  // Toggle mute
  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }, [isMuted])

  // Set playback rate
  const setPlaybackRate = useCallback((rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate
      setPlaybackRateState(rate)
    }
  }, [])

  // Frame navigation (assuming 30fps)
  const fps = 30
  const frameDuration = 1 / fps

  const nextFrame = useCallback(() => {
    pause()
    seekRelative(frameDuration)
  }, [pause, seekRelative, frameDuration])

  const prevFrame = useCallback(() => {
    pause()
    seekRelative(-frameDuration)
  }, [pause, seekRelative, frameDuration])

  // Event handlers
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime)
      onTimeUpdate?.(video.currentTime)
    }
    const handleDurationChange = () => {
      setDuration(video.duration)
      onDurationChange?.(video.duration)
    }
    const handleEnded = () => {
      setIsPlaying(false)
      onEnded?.()
    }
    const handleLoadedMetadata = () => {
      setIsLoading(false)
      setDuration(video.duration)
      onLoadedMetadata?.()
    }
    const handleWaiting = () => setIsLoading(true)
    const handleCanPlay = () => setIsLoading(false)

    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)
    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('durationchange', handleDurationChange)
    video.addEventListener('ended', handleEnded)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('waiting', handleWaiting)
    video.addEventListener('canplay', handleCanPlay)

    return () => {
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('durationchange', handleDurationChange)
      video.removeEventListener('ended', handleEnded)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      video.removeEventListener('waiting', handleWaiting)
      video.removeEventListener('canplay', handleCanPlay)
    }
  }, [onTimeUpdate, onDurationChange, onEnded, onLoadedMetadata])

  return {
    videoRef,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    isLoading,
    playbackRate,
    play,
    pause,
    toggle,
    seek,
    seekRelative,
    setVolume,
    toggleMute,
    setPlaybackRate,
    nextFrame,
    prevFrame,
  }
}
