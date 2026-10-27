import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { Downsampler, encodePCM, decodePCM, createBrowserAudio } from './audio/pcm.js'
import { createVoice } from './voice.js'

function fixture(audioOverrides = {}) {
  const changes = [], sent = [], timers = new Map()
  let id = 0
  const audio = { closed:0, stopped:0, cleared:0, frames:null, async open(){}, async prepareMicrophone(){return true}, async record(fn){this.frames=fn; return true},
    stopRecording(){this.stopped++}, play(){}, async enablePlayback(){}, clearPlayback(){this.cleared++}, remainingMs(){return 0}, close(){this.closed++}, ...audioOverrides }
  const ws = {readyState:1, bufferedAmount:0, send(value){sent.push(value)},close(){this.closed=true}}
  const voice = createVoice({ socketFactory:()=>ws,audioFactory:()=>audio,onChange:x=>changes.push(x),
    later:(fn,ms)=>{const key=++id;timers.set(key,{fn:()=>{timers.delete(key);fn()},ms}); return key},cancel:key=>timers.delete(key) })
  const event = value => ws.onmessage?.({data:typeof value==='object' && !(value instanceof ArrayBuffer) ? JSON.stringify(value):value})
  const ready = async () => {await voice.start('ws://local/api/voice','fictional-id');ws.onopen();event({type:'ready',mode:'mock',setup_confirmed:true})}
  return {voice,ws,audio,changes,sent,timers,event,ready}
}

test('PCM is little endian, clipped, finite and rejects incomplete samples',()=>{
  const encoded=encodePCM([-2,-1,0,1,2,NaN])
  assert.deepEqual([...new Uint8Array(encoded)],[0,128,0,128,0,0,255,127,255,127,0,0])
  assert.equal(decodePCM(encoded)[0],-1)
  assert.throws(()=>decodePCM(new ArrayBuffer(3)))
})

test('48k and 44.1k streaming resampling preserves chunk boundaries and counts',()=>{
  for(const rate of [48000,44100]){
    const input=Float32Array.from({length:rate},(_,i)=>Math.sin(i/50))
    const full=new Downsampler(rate).push(input), stream=new Downsampler(rate), pieces=[]
    for(let i=0;i<input.length;i+=127)pieces.push(...stream.push(input.slice(i,i+127)))
    assert.equal(full.length,16000)
    assert.deepEqual(Float32Array.from(pieces),full)
  }
  assert.throws(()=>new Downsampler(8000))
})

test('explicit talk, end, playback drain and stop; no transcript/content persistence',async()=>{
  const f=fixture();await f.ready()
  assert.equal(f.voice.state,'ready')
  await f.voice.talk();assert.equal(f.voice.state,'recording')
  f.audio.frames(new ArrayBuffer(640));f.voice.endTurn()
  assert.equal(f.audio.stopped,1);assert.equal(f.voice.state,'waiting')
  f.event(new ArrayBuffer(9600));assert.equal(f.voice.state,'speaking')
  f.event({type:'turn_complete'});assert.equal(f.voice.state,'playback')
  const drain=[...f.timers.values()].find(x=>x.ms===30);drain.fn()
  assert.ok(f.sent.some(x=>typeof x==='string' && x.includes('playback_done')))
  f.event({type:'ready'});assert.equal(f.voice.state,'ready')
  f.voice.stop();assert.equal(f.audio.closed,1);assert.equal(f.ws.closed,true);assert.equal(f.timers.size,0)
})

test('late frames and results after Stop/Support/navigation cannot play or reactivate mic',async()=>{
  let played=0
  const f=fixture({play(){played++}});await f.ready();await f.voice.talk()
  const late=f.ws.onmessage, frame=f.audio.frames
  f.voice.stop('Support opened')
  late({data:new ArrayBuffer(640)});frame(new ArrayBuffer(640))
  assert.equal(played,0);assert.equal(f.voice.state,'stopped');assert.equal(f.audio.closed,1)
})

test('permission denial and audio setup failure are finite errors',async()=>{
  const f=fixture({async record(){throw new Error('denied')}});await f.ready();await f.voice.talk()
  assert.equal(f.voice.state,'error');assert.equal(f.ws.closed,true)
  const g=fixture({async open(){throw new Error('unsupported')}})
  await g.voice.start('ws://local','id');assert.equal(g.voice.state,'error')
})

test('setup, response, session and utterance timers enforce finite boundaries',async()=>{
  const f=fixture();await f.voice.start('ws://local','id')
  assert.ok([...f.timers.values()].some(x=>x.ms===300000))
  ;[...f.timers.values()].find(x=>x.ms===10000).fn()
  assert.equal(f.voice.state,'error')
  const g=fixture();await g.ready();await g.voice.talk()
  ;[...g.timers.values()].find(x=>x.ms===20000).fn()
  assert.equal(g.voice.state,'waiting')
  ;[...g.timers.values()].find(x=>x.ms===15000).fn()
  assert.equal(g.voice.state,'error')
})

test('backend disconnect, malformed event, output cap, and backpressure close audio',async()=>{
  for(const kind of ['disconnect','malformed','cap','pressure']){
    const f=fixture();await f.ready();await f.voice.talk()
    if(kind==='pressure'){f.ws.bufferedAmount=32001;f.audio.frames(new ArrayBuffer(640))}
    else {f.voice.endTurn();if(kind==='disconnect')f.ws.onclose();if(kind==='malformed')f.event('{bad');if(kind==='cap')f.event(new ArrayBuffer(720002))}
    assert.ok(['error','stopped'].includes(f.voice.state));assert.equal(f.audio.closed,1)
  }
})

test('stop during permission prompt stops late acquired microphone tracks',async()=>{
  let resolve, stopped=0, closed=0
  class Context{
    state='running';audioWorklet={async addModule(){}};async resume(){};async close(){this.state='closed';closed++}
  }
  const audio=createBrowserAudio({Context,Worklet:class{},media:{getUserMedia:()=>new Promise(r=>{resolve=r})}})
  await audio.open();const pending=audio.record(()=>{})
  audio.close();resolve({getTracks:()=>[{stop(){stopped++}}]})
  assert.equal(await pending,false);assert.equal(stopped,1);assert.equal(closed,1)
})

test('voice is optional outside grounding, Support and Stop stop voice before navigation',()=>{
  const app=readFileSync(new URL('./App.vue',import.meta.url),'utf8')
  assert.match(app,/\['SUPPORT', 'STOP', 'HOME', 'BEGIN', 'PAUSE'\].*voicePanel.value\?\.stop\(\)/)
  assert.match(app,/v-if="experience.finished"[^\n]*voiceOpen = true/)
  const panel=readFileSync(new URL('./components/VoicePanel.vue',import.meta.url),'utf8')
  assert.match(panel,/document.hidden.*stop\(\)/)
  assert.match(panel,/No Gemini call is made/)
  assert.match(panel,/No audio or transcripts are saved/)
  const chat=readFileSync(new URL('./components/ChatPanel.vue',import.meta.url),'utf8')
  assert.match(chat,/<VoicePanel ref="voicePanel" embedded/)
  assert.match(chat,/<form @submit.prevent="send">/)
  assert.match(chat,/voicePanel.value\?\.stop\(\)/)
  assert.match(panel,/Enable assistant audio/)
  for(const text of ['RTCPeerConnection','oai-events','/sdp']){
    assert.equal((chat+panel+readFileSync(new URL('./voice.js',import.meta.url),'utf8')).includes(text),false)
  }
})

test('Start requests permission before socket; active requires confirmed provider setup',async()=>{
  let grant
  const f=fixture({prepareMicrophone:()=>new Promise(resolve=>{grant=resolve})})
  const starting=f.voice.start('ws://local','id')
  await Promise.resolve()
  assert.equal(f.changes.at(-1).connection,'permission')
  assert.equal(f.sent.length,0)
  assert.equal(f.ws.onopen,undefined)
  grant(true);await starting
  assert.equal(f.changes.at(-1).connection,'connecting')
  f.ws.onopen()
  assert.equal(f.changes.at(-1).connection,'connecting')
  f.event({type:'ready',mode:'mock',setup_confirmed:true})
  assert.equal(f.changes.at(-1).connection,'active')
  assert.equal(f.changes.at(-1).microphone,'muted')
  await f.voice.talk()
  assert.equal(f.changes.at(-1).microphone,'active')
  f.voice.endTurn()
  assert.equal(f.changes.at(-1).microphone,'muted')
  f.voice.stop()
  assert.ok(f.changes.some(x=>x.connection==='closing'))
  assert.equal(f.changes.at(-1).connection,'closed')
})

test('Start microphone denial never opens a socket; malformed setup is never active',async()=>{
  const f=fixture({async prepareMicrophone(){throw new Error('permission denied')}})
  await f.voice.start('ws://local','id')
  assert.equal(f.ws.onopen,undefined)
  assert.equal(f.changes.at(-1).connection,'failure')
  const g=fixture();await g.voice.start('ws://local','id')
  g.event({type:'ready',mode:'mock'})
  assert.equal(g.changes.at(-1).connection,'failure')
  assert.equal(g.changes.some(x=>x.connection==='active'),false)
})

test('socket error or abnormal closure becomes failure; normal closure becomes closed',async()=>{
  for(const code of ['error',1006,1000]){
    const f=fixture();await f.ready()
    if(code==='error')f.ws.onerror();else f.ws.onclose({code})
    assert.equal(f.changes.at(-1).connection,code===1000?'closed':'failure')
    assert.equal(f.audio.closed,1)
  }
})

test('blocked playback waits for explicit Enable gesture before reporting playback done',async()=>{
  let enabled=0
  const f=fixture({play(){return false},async enablePlayback(){enabled++}})
  await f.ready();await f.voice.talk();f.voice.endTurn()
  f.event(new ArrayBuffer(640));f.event({type:'turn_complete'})
  assert.equal(f.changes.at(-1).audioBlocked,true)
  assert.equal([...f.timers.values()].some(x=>x.ms===30),false)
  assert.equal(enabled,0)
  await f.voice.enableAudio()
  assert.equal(enabled,1);assert.equal(f.changes.at(-1).audioBlocked,false)
  ;[...f.timers.values()].find(x=>x.ms===30).fn()
  assert.ok(f.sent.some(x=>typeof x==='string'&&x.includes('playback_done')))
})

test('interruption clears scheduled/blocked audio and rejects late output without reconnect',async()=>{
  const f=fixture({play(){return false}})
  await f.ready();await f.voice.talk();f.voice.endTurn()
  f.event(new ArrayBuffer(640))
  const late=f.ws.onmessage
  f.event({type:'interrupted'})
  assert.equal(f.audio.cleared,1);assert.equal(f.audio.closed,1);assert.equal(f.timers.size,0)
  late({data:new ArrayBuffer(640)})
  assert.equal(f.changes.at(-1).connection,'closed')
  assert.equal(f.changes.at(-1).audioBlocked,false)
})

test('actual browser-audio adapter uses exact constraints, muted tracks and a bounded recoverable queue',async()=>{
  const constraints=[], nodes=[]
  let allowed=false, requested=0, stopped=0
  const track={enabled:true,stop(){stopped++}}
  class Context{
    state='suspended';currentTime=0;audioWorklet={async addModule(){}}
    async resume(){if(allowed)this.state='running';else throw new Error('autoplay blocked')}
    async close(){this.state='closed'}
    createMediaStreamSource(){return {connect(){},disconnect(){}}}
    createBuffer(channels,length,rate){assert.equal(rate,24000);return {duration:length/rate,copyToChannel(){}}}
    createBufferSource(){const node={connect(){},disconnect(){},start(){},stop(){node.stopped=true}};nodes.push(node);return node}
  }
  class Worklet{port={close(){}};connect(){};disconnect(){}}
  const audio=createBrowserAudio({Context,Worklet,media:{async getUserMedia(value){requested++;constraints.push(value);return {getTracks:()=>[track]}}}})
  await audio.open();assert.equal(requested,0)
  await audio.prepareMicrophone();assert.deepEqual(constraints,[{audio:true,video:false}]);assert.equal(track.enabled,false)
  await audio.record(()=>{});assert.equal(track.enabled,true);assert.equal(requested,1)
  audio.stopRecording();assert.equal(stopped,1)
  assert.equal(audio.play(new ArrayBuffer(640)),false)
  assert.equal(nodes.length,0)
  allowed=true;await audio.enablePlayback()
  assert.equal(nodes.length,1)
  audio.clearPlayback();assert.equal(nodes[0].stopped,true);assert.equal(audio.remainingMs(),0)
  audio.close()
})

test('blocked audio over one second fails instead of accumulating; recovery cannot revive stopped session',async()=>{
  class Context{state='suspended';audioWorklet={async addModule(){}};async resume(){};async close(){this.state='closed'}}
  const audio=createBrowserAudio({Context,Worklet:class{},media:{getUserMedia(){}}})
  await audio.open();assert.equal(audio.play(new ArrayBuffer(48000)),false)
  assert.throws(()=>audio.play(new ArrayBuffer(2)),/one second/)
  audio.clearPlayback();assert.equal(audio.play(new ArrayBuffer(2)),false);audio.close()
  let resume
  const f=fixture({play(){return false},enablePlayback:()=>new Promise(resolve=>{resume=resolve})})
  await f.ready();await f.voice.talk();f.voice.endTurn();f.event(new ArrayBuffer(640));f.event({type:'turn_complete'})
  const enabling=f.voice.enableAudio();f.voice.stop();resume();await enabling
  assert.equal(f.voice.state,'stopped');assert.equal(f.timers.size,0)
})

test('Mute ends one manual input activity, keeps socket/playback and does not forward late frames',async()=>{
  const f=fixture();await f.ready();await f.voice.unmute()
  const lateFrame=f.audio.frames
  lateFrame(new ArrayBuffer(640))
  f.voice.mute();f.voice.mute()
  const before=f.sent.length
  lateFrame(new ArrayBuffer(640))
  assert.equal(f.sent.length,before)
  assert.equal(f.sent.filter(x=>typeof x==='string'&&JSON.parse(x).type==='activity_end').length,1)
  assert.equal(f.sent.some(x=>typeof x==='string'&&x.includes('audioStreamEnd')),false)
  assert.equal(f.ws.closed,undefined);assert.equal(f.audio.closed,0);assert.equal(f.audio.cleared,0)
  f.event(new ArrayBuffer(640));f.voice.mute()
  assert.equal(f.voice.state,'speaking');assert.equal(f.audio.cleared,0)
  f.event({type:'turn_complete'})
  ;[...f.timers.values()].find(x=>x.ms===30).fn()
  f.event({type:'ready'})
  await f.voice.unmute()
  assert.equal(f.voice.state,'recording')
  lateFrame(new ArrayBuffer(640))
  assert.equal(f.sent.filter(x=>x instanceof ArrayBuffer).length,1,'old turn callback cannot feed new turn')
})

test('duplicate Starts and repeated Ends are idempotent; each accepted Start has fresh resources',async()=>{
  let resolveOpen
  const audios=[], sockets=[], changes=[]
  const voice=createVoice({audioFactory:()=>{
    const a={closed:0,open:()=>audios.length===1?new Promise(r=>{resolveOpen=r}):Promise.resolve(),async prepareMicrophone(){return true},close(){this.closed++}}
    audios.push(a);return a
  },socketFactory:()=>{const ws={readyState:1,send(){},close(){this.closed=true}};sockets.push(ws);return ws},onChange:x=>changes.push(x)})
  const first=voice.start('ws://local','id')
  assert.equal(await voice.start('ws://local','id'),false)
  assert.equal(audios.length,1)
  voice.end();voice.end();assert.equal(audios[0].closed,1)
  await voice.start('ws://local','id')
  assert.equal(audios.length,2);assert.equal(sockets.length,1)
  const current=voice.state
  resolveOpen();await first
  assert.equal(sockets.length,1);assert.equal(voice.state,current)
  const lateOpen=sockets[0].onopen,lateSetup=sockets[0].onmessage
  voice.end();voice.end()
  lateOpen();lateSetup({data:JSON.stringify({type:'ready',mode:'mock',setup_confirmed:true})})
  assert.equal(voice.state,'stopped');assert.equal(audios[1].closed,1)
})

test('End stops resources once even when an individual audio close throws',async()=>{
  const f=fixture({close(){this.closed++;throw new Error('resource failure')}})
  await f.ready();f.voice.end();f.voice.end()
  assert.equal(f.audio.closed,1);assert.equal(f.ws.closed,true);assert.equal(f.timers.size,0)
})

test('Mute cancels an in-flight Unmute permission result without closing the session',async()=>{
  let resolveRecord
  const f=fixture({record:()=>new Promise(resolve=>{resolveRecord=resolve})})
  await f.ready();const unmuting=f.voice.unmute();f.voice.mute()
  resolveRecord(true);await unmuting
  assert.equal(f.voice.state,'ready')
  assert.equal(f.sent.some(x=>typeof x==='string'&&x.includes('activity_start')),false)
  assert.equal(f.audio.closed,0);assert.equal(f.ws.closed,undefined)
})

test('audio adapter discards late media permission after Mute, not just End',async()=>{
  let resolve, stopped=0
  class Context{state='running';audioWorklet={async addModule(){}};async resume(){};async close(){}}
  const audio=createBrowserAudio({Context,Worklet:class{},media:{getUserMedia:()=>new Promise(r=>{resolve=r})}})
  await audio.open();const pending=audio.prepareMicrophone();audio.stopRecording()
  resolve({getTracks:()=>[{stop(){stopped++}}]})
  assert.equal(await pending,false);assert.equal(stopped,1);audio.close()
})

test('300-second client maximum and all external cleanup reasons release audio/socket/timers',async()=>{
  for(const reason of ['maximum','Emergency Support','navigation/unmount','page exit','failure']){
    const f=fixture();await f.ready();await f.voice.unmute()
    const late=f.ws.onmessage
    if(reason==='maximum')[...f.timers.values()].find(x=>x.ms===300000).fn()
    else if(reason==='failure')f.ws.onerror()
    else f.voice.end(reason)
    late({data:JSON.stringify({type:'ready',mode:'mock',setup_confirmed:true})})
    assert.equal(f.audio.closed,1);assert.equal(f.ws.closed,true);assert.equal(f.timers.size,0)
    assert.ok(['closed','failure'].includes(f.changes.at(-1).connection))
  }
  const panel=readFileSync(new URL('./components/VoicePanel.vue',import.meta.url),'utf8')
  assert.match(panel,/onUnmounted\(\(\) => \{ stop\(\)/)
  assert.match(panel,/addEventListener\('pagehide', stop\)/)
  assert.match(panel,/function stop\(\) \{ client.end\(\) \}/)
  assert.match(panel,/>Mute<\/button>/);assert.match(panel,/>End<\/button>/)
})

test('actual End releases tracks, nodes, worklet port and context even if one resource throws',async()=>{
  const released={track:0,source:0,worklet:0,port:0,playback:0,context:0}
  class Context{
    state='running';currentTime=0;audioWorklet={async addModule(){}}
    async resume(){};async close(){released.context++;this.state='closed'}
    createMediaStreamSource(){return {connect(){},disconnect(){released.source++}}}
    createBuffer(_,length,rate){return {duration:length/rate,copyToChannel(){}}}
    createBufferSource(){return {connect(){},start(){},stop(){throw new Error('already ended')},disconnect(){released.playback++}}}
  }
  class Worklet{port={close(){released.port++}};connect(){};disconnect(){released.worklet++}}
  const audio=createBrowserAudio({Context,Worklet,media:{async getUserMedia(){return {getTracks:()=>[
    {stop(){throw new Error('track fault')}},{stop(){released.track++}}
  ]}}}})
  await audio.open();await audio.prepareMicrophone();await audio.record(()=>{});audio.play(new ArrayBuffer(640))
  audio.close();audio.close()
  assert.deepEqual(released,{track:1,source:1,worklet:1,port:1,playback:1,context:1})
})
