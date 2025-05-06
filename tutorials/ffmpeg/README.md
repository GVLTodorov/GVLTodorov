# FFmpeg Cheat Sheet

## Replace audio

![image](https://user-images.githubusercontent.com/51453974/224025856-388fb6b0-33b4-4c1a-8668-8f9678fbb1d4.png)

```ffmpeg -i video.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -shortest output.mp4```

* The -map option allows you to manually select streams / tracks. See FFmpeg Wiki: Map for more info.
* This example uses -c:v copy to stream copy (mux) the video. No re-encoding of the video occurs. Quality is preserved and the process is fast.
* If your input audio format is compatible with the output format then change -c:v copy to -c copy to stream copy both the video and audio.
* If you want to re-encode video and audio then remove -c:v copy / -c copy.
* The -shortest option will make the output the same duration as the shortest input.

## Add audio

![image](https://user-images.githubusercontent.com/51453974/224026183-0db81e71-2811-4522-8d21-600b0b2435d1.png)

```ffmpeg -i video.mkv -i audio.mp3 -map 0 -map 1:a -c:v copy -shortest output.mkv```

* The -map option allows you to manually select streams / tracks. See FFmpeg Wiki: Map for more info.
* This example uses -c:v copy to stream copy (mux) the video. No re-encoding of the video occurs. Quality is preserved and the process is fast.

> If your input audio format is compatible with the output format then change -c:v copy to -c copy to stream copy both the video and audio.

> If you want to re-encode video and audio then remove -c:v copy / -c copy.

* The -shortest option will make the output the same duration as the shortest input.

## Mixing/Combining two audio inputs into one

![image](https://user-images.githubusercontent.com/51453974/224026498-58c1d09e-0553-4654-a31f-e04c29416b71.png)

```ffmpeg -i video.mkv -i audio.m4a -filter_complex "[0:a][1:a]amerge=inputs=2[a]" -map 0:v -map "[a]" -c:v copy -ac 2 -shortest output.mkv```

> https://trac.ffmpeg.org/wiki/AudioChannelManipulation

## Generate silent audio

```ffmpeg -i video.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -c:v copy -shortest output.mp4```

## Cheat Sheet

```
ffmpeg -i a.m4a -map 0:a:0 -codec:a aac output.aac
ffmpeg -i a.mkv -i output.aac -c:v copy -map 0:v:0 -map 1:a:0  -metadata:s:a:0 language=bul new.mkv
ffmpeg -i a.mkv -i output.aac -map 0 -map 1:a -c:v copy -shortest -metadata:s:a:1 language=bul new.mkv
```

