import argparse
import asyncio
import logging
from threading import Thread
import math
import pyaudio
import platform
import time
from bitarray import bitarray

import sounddevice as sd
sample_rate = 44100
key = []
# sample_rate = 8196

import cv2
import numpy as np
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    RTCDataChannel,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaStreamTrack, MediaRelay
from aiortc.rtp import RtpPacket
from aiortc.mediastreams import VideoStreamTrack, AudioStreamTrack
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from av import VideoFrame, AudioFrame, Packet
from av.frame import Frame

import sys
import os
import pathlib

sys.path.insert(0, pathlib.Path(__file__).parent.parent.resolve().as_posix())
from utils.encryption import AESEncryption, RandomKeyGenerator, KeyGeneratorFactory, EncryptionFactory, EncryptionScheme

# MediaStreamTrack.stop = lambda: None

# def encode(data: bytes, key: bitarray):
#     if key != None and key[0] == 0:
#         return data[1000:] + data[:1000]
#     return data

# def decode(data: bytes, key: bitarray):
#     if key != None and key[0] == 0:
#         return data[-1000:] + data[:-1000]
#     return data

class EncodedVideoStreamTrack(VideoStreamTrack):
    def __init__(self, source: VideoStreamTrack, encryption: EncryptionScheme=None):
        super().__init__()
        self.kind = source.kind
        self.source = source
        self.encryption = encryption
        self.key_queue = None
        key_gen = KeyGeneratorFactory().create_key_generator("DEBUG")
        key_gen.generate_key(key_length=128)
        self.key = key_gen.get_key().tobytes()

    async def recv(self):
        # VideoFrame -> NDArray -> bytes -> encoded bytes -> encoded NDArray -> encoded VideoFrame
        frame: VideoFrame = await self.source.recv()
        if self.encryption is None:
            return frame
        
        data = frame.to_ndarray(format="yuyv422")
        shape = data.shape

        # print(len(data.tobytes()), len(self.encode(data.tobytes()[:-16], self.key.tobytes())))
        # encryption = EncryptionFactory().create_encryption_scheme("AES")
        # data = self.encode(data.tobytes()[:-32], self.key.tobytes())
        data = self.encryption.encrypt(data.tobytes(), self.key)
        # data = encryption.encrypt(data.tobytes()[:-32], self.key.tobytes())

        data = np.frombuffer(data, dtype=np.uint8).reshape(shape)
        # print(data.shape)
        # print("send", np.average(data[:,:,0]), np.average(data[:,:,1]), np.average(data[:,:,2]))

        packet = VideoFrame.from_ndarray(data, format="yuyv422")

        # data = packet.to_ndarray(format="yuyv422")
        # # print("recv", np.average(data[:,:,0])/np.average(data), np.average(data[:,:,1])/np.average(data), np.average(data[:,:,2])/np.average(data), np.average(data[:,:,3])/np.average(data))
        
        # shape = data.shape
        # # print(shape)

        # # if not key_queue.empty():
        # #     key = await key_queue.get()
        # # print("vid start")
        # # print(len(data.tobytes()))
        # encryption = EncryptionFactory().create_encryption_scheme("AES")
        # data = encryption.decrypt(data.tobytes(), self.key.tobytes())
        # # print(data.tobytes()[:10])
        # # print(len(data + b'0' * (16)))
        # data = np.frombuffer(data, dtype=np.uint8).reshape(shape)

        # packet = VideoFrame.from_ndarray(data, format="yuyv422")





        packet.pts, packet.time_base = await self.next_timestamp()
        # print("sent", packet.pts, data)
        # tdata.append((packet.time_base, packet.pts))

        # data = packet.to_ndarray(format="yuyv422")
        # print("INCOMP", data.shape, tdata.shape, np.sum(data == tdata))
        
        return packet
    
class EncodedAudioStreamTrack(AudioStreamTrack):
    def __init__(self, source: AudioStreamTrack, encryption: EncryptionScheme=None):
        super().__init__()
        self.kind = source.kind
        self.source = source
        self.encryption = encryption
        self.key_queue = None
        key_gen = KeyGeneratorFactory().create_key_generator("RANDOM")
        key_gen.generate_key(128)
        self.key = key_gen.get_key().tobytes()

    async def recv(self):
        frame = await self.source.recv()
        if self.encryption is None:
            return frame
        
        data = frame.to_ndarray(format="s16", layout='mono', dtype='<i2')
        shape = data.shape
        # print(data.shape, data.dtype)

        # if not self.key_queue.empty():
        #     self.key = await self.key_queue.get()

        data = self.encryption.encrypt(data.tobytes(), self.key)
        data = np.frombuffer(data, dtype='<i2').reshape(shape)
        # print(data.shape, data.dtype)
        packet = AudioFrame.from_ndarray(data, format="s16", layout='mono')
        packet.framerate = frame.framerate
        packet.pts, packet.time_base = await self.next_timestamp()
        # print(packet)
        
        return packet

async def run(pc: RTCPeerConnection, track: MediaStreamTrack, signaling, role, encryption: EncryptionScheme=None):
    key_channel = None
    video_channel = None
    key_queue = asyncio.Queue()
    track.key_queue = key_queue
    # key = None
    key_gen = KeyGeneratorFactory().create_key_generator("RANDOM")
    key_gen.generate_key(key_length=128)
    key = key_gen.get_key().tobytes()

    def add_tracks():
        pc.addTrack(track)

    async def video_track(track: EncodedVideoStreamTrack):
        nonlocal key
        local_track = EncodedVideoStreamTrack(track, encryption=encryption)
        # track.add_listener("event", lambda event: print(event))
        while True:
            # encoded VideoFrame -> encoded NDArray -> encoded bytes -> bytes -> NDArray
            # print("track execution %s" % track.kind)
            frame = await local_track.recv()
            # print("track receive %s" % track.kind)

            data = frame.to_ndarray(format="yuyv422")
            print("received", frame.pts, data)
            # print("recv", np.average(data[:,:,0]), np.average(data[:,:,1]), np.average(data[:,:,2]))
            
            shape = data.shape
            # print(shape)

            # if not key_queue.empty():
            #     key = await key_queue.get()
            print("vid start")
            if encryption is not None and False:
                # print(len(data.tobytes()))
                data = encryption.decrypt(data.tobytes(), key.tobytes())
                # print(data.tobytes()[:10])
                # print(len(data + b'0' * (16)))
                data = np.frombuffer(data, dtype=np.uint8).reshape(shape)
                # data = np.frombuffer(data  + b'\0' * 32, dtype=np.uint8).reshape(shape)
            # print("vid end")
            print(shape)
            img = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_YUYV)

            cv2.imshow("recv", img)
            cv2.waitKey(1)
            # break

    async def audio_track(track: EncodedAudioStreamTrack):
        nonlocal key
        sdstream = sd.OutputStream(samplerate=sample_rate*2, channels=1, dtype='int16')
        sdstream.start()
        # buffer = np.array([])
        while True:
            # print("track execution %s" % track.kind)
            frame = await track.recv()
            # print("track receive %s" % track.kind)
            data = frame.to_ndarray()
            shape = data.shape

            if not key_queue.empty():
                key = await key_queue.get()

            print("aud start")
            if encryption is not None:
                data = encryption.decrypt(data.tobytes(), key.tobytes())
                data = np.frombuffer(data, dtype=np.int16).reshape(shape)
            print("aud end")

            # print(data.shape, data)
            data = data[0]
            sdstream.write(data)
    
    @pc.on("track")
    async def on_track(track: MediaStreamTrack):
        print("Receiving %s" % track.kind)
        if track.kind == "video":
            # await asyncio.ensure_future(video_track(track))
            pass

        if track.kind == "audio":
            # await asyncio.ensure_future(audio_track(track))
            pass

    # @key_channel.on("open")
    # async def on_open():
    #     asyncio.ensure_future(send_keys(key_channel))

    # connect signaling

    async def send_keys():
        print('send_keys')
        key_gen = KeyGeneratorFactory().create_key_generator("RANDOM")
        while True:
            key_gen.generate_key(128)
            key = key_gen.get_key().tobytes()
            key_channel.send(key)
            await key_queue.put(key)
            print(key, key_queue.qsize())
            await asyncio.sleep(1)

    async def send_video():
        nonlocal key
        print('send_video')
        cam = cv2.VideoCapture(0)
        res = (160, 120)
        res = (640, 480)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
        # cam.set(cv2.CV_CAP_PROP_FRAME_WIDTH, 640)
        # cam.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, 480)
        while True:
            if not key_queue.empty():
                key = key_queue.get_nowait()
            # frame = await track.recv()
            result, image = cam.read()
            # print(image.shape, type(image), image.dtype)
            
            data = image.tobytes()
            # data = frame.to_ndarray(format="bgr24").tobytes()
            # data = frame.to_ndarray(format="yuyv422").tobytes()

            if encryption is not None:
                data = encryption.encrypt(data, key)
            # print("send", len(data))
            video_channel.send(data)
            # await video_channel._RTCDataChannel__transport._data_channel_flush()
            # await video_channel._RTCDataChannel__transport._transmit()
            # await asyncio.sleep(1/25)
            await asyncio.sleep(1/10)
            

    @pc.on("datachannel")
    def on_datachannel(channel: RTCDataChannel):
        print("New Data Channel: " + channel.label)
        if channel.label == track.kind + " key":
            key_channel = channel

            @key_channel.on("message")
            async def on_message(message):
                key = message
                await key_queue.put(key)
                # print(key, key_queue.qsize())

        elif channel.label == "video data":
            video_channel = channel

            @video_channel.on("message")
            async def on_message(message):
                # print("recv", len(message))
                nonlocal key
                # print("recv", message)
                if not key_queue.empty():
                    key = key_queue.get_nowait()

                data = message
                if encryption is not None:
                    # print(len(data.tobytes()))
                    data = encryption.decrypt(data, key)
                    # print(data.tobytes()[:10])
                    # print(len(data + b'0' * (16)))
                shape = (480, 640, 3)
                # shape = (1080, 1920, 3)
                data = np.frombuffer(data, dtype=np.uint8).reshape(shape)
                    # data = np.frombuffer(data  + b'\0' * 32, dtype=np.uint8).reshape(shape)
                    # print("vid end")
                # data = cv2.cvtColor(data, cv2.COLOR_YUV2BGR_YUYV)

                cv2.imshow("recv", data)
                cv2.waitKey(1)

    await signaling.connect()

    print(track.kind +  " ready for signaling")

    if role == "offer":
        # send offer
        key_channel = pc.createDataChannel(track.kind + " key")
        @key_channel.on("open")
        async def on_open():
            asyncio.ensure_future(send_keys())
            pass

        video_channel = pc.createDataChannel(track.kind + " data")
        @video_channel.on("open")
        async def on_open():
            asyncio.ensure_future(send_video())
        
        # add_tracks()
        await pc.setLocalDescription(await pc.createOffer())
        await signaling.send(pc.localDescription)


    # consume signaling
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)

            if obj.type == "offer":
                # send answer

                # video_channel = pc.createDataChannel(track.kind + " data")
                # @video_channel.on("open")
                # async def on_open():
                #     asyncio.ensure_future(send_video())
                    
                # add_tracks()
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break

        await pc.getStats()

if __name__ == "__main__":

    # encryption = EncryptionFactory().create_encryption_scheme("AES")
    # key_gen = KeyGeneratorFactory().create_key_generator("DEBUG")
    # key_gen.generate_key(key_length=128)
    # key = key_gen.get_key()
    # strs = [b"hello", b"world", b"this", b"is", b"a", b"test", b"string"]
    # for s in strs:
    #     # print(s, encryption.encrypt(s, key).tobytes())
    #     # print(s, encryption.decrypt(encryption.encrypt(s, key), key).tobytes())
    #     print(s, encryption.decrypt(encryption.encrypt(s, key.tobytes()), key.tobytes()))

    # exit(0)

    # key_gen = RandomKeyGenerator()
    # key_gen.generate_key(128)
    # key = key_gen.get_key()
    # print(key)

    parser = argparse.ArgumentParser(description="Video stream from the command line")
    parser.add_argument("role", choices=["offer", "answer"])
    parser.add_argument("--verbose", "-v", action="count")
    
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Create signaling
    HOST = '127.0.0.1'
    # HOST = '100.80.231.89'
    # HOST = '192.168.68.72'
    # HOST = '128.54.191.80'
    # HOST = '100.115.52.50'
    # HOST = '0.0.0.0'
    PORT = '65431'
    signaling_parser = argparse.ArgumentParser()
    add_signaling_arguments(signaling_parser)
    signaling_args = signaling_parser.parse_args(
        ['--signaling', 'tcp-socket', '--signaling-host', HOST, '--signaling-port', PORT]
    )
    vsignaling = create_signaling(signaling_args)
    vpc = RTCPeerConnection()


    PORT = '65432'
    signaling_args = signaling_parser.parse_args(
        ['--signaling', 'tcp-socket', '--signaling-host', HOST, '--signaling-port', PORT]
    )
    asignaling = create_signaling(signaling_args)
    apc = RTCPeerConnection()
    
    # Video/Audio options
    voptions = {
        'framerate': '30', 
        'video_size': '640x480',
        # 'pixel_format': 'bgr0',
        'pixel_format': 'yuyv422',
    }
    aoptions = {
        'sample_rate': str(sample_rate)
    }

    # Create player
    if platform.system() == 'Darwin':
        video_player = MediaPlayer('default:none', format='avfoundation', options=voptions)
        audio_player = MediaPlayer('none:default', format='avfoundation', options=aoptions)
        # aplayer = MediaPlayer('sin.wav', format=None, options=aoptions)
    elif platform.system() == 'Windows':
        video_player = MediaPlayer('video=Integrated Camera', format='dshow', options=voptions)
        audio_player = MediaPlayer('audio=Microphone (Realtek(R) Audio)', format='dshow', options=aoptions)

    encryption = EncryptionFactory().create_encryption_scheme("AES")
    # video_track = EncodedVideoStreamTrack(video_player.video, encryption=encryption)
    # audio_track = EncodedAudioStreamTrack(audio_player.audio, encryption=None)
    video_track = video_player.video
    audio_track = audio_player.audio

    # Run event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete( 
            asyncio.gather(
                run(
                    pc=vpc,
                    track=video_track,
                    signaling=vsignaling,
                    role=args.role,
                    encryption=encryption,
                ),
                # run(
                #     pc=apc,
                #     track=audio_track,
                #     signaling=asignaling,
                #     role=args.role,
                #     encryption=None,
                # )
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        # cleanup
        loop.run_until_complete(vsignaling.close())
        loop.run_until_complete(vpc.close())
        loop.run_until_complete(asignaling.close())
        loop.run_until_complete(apc.close())

    print("exit")