const canvas=document.createElement('canvas');
document.body.appendChild(canvas);
canvas.style.position='fixed';
canvas.style.top='0';canvas.style.left='0';
canvas.style.width='100%';canvas.style.height='100%';
canvas.style.zIndex='-1';
const ctx=canvas.getContext('2d');
let width=canvas.width=window.innerWidth;
let height=canvas.height=window.innerHeight;
window.addEventListener('resize',()=>{width=canvas.width=window.innerWidth;height=canvas.height=window.innerHeight;});
class Particle{constructor(){this.reset();}reset(){this.x=Math.random()*width;this.y=Math.random()*height;this.vx=(Math.random()-0.5)*0.5;this.vy=(Math.random()-0.5)*0.5;this.size=Math.random()*2+1;this.color=`hsl(${Math.random()*360},100%,75%)`;}update(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>width||this.y<0||this.y>height)this.reset();}draw(){ctx.beginPath();ctx.arc(this.x,this.y,this.size,0,Math.PI*2);ctx.fillStyle=this.color;ctx.shadowBlur=10;ctx.shadowColor=this.color;ctx.fill();}}
const particles=[];
for(let i=0;i<120;i++)particles.push(new Particle());
function animate(){ctx.fillStyle='rgba(30,0,50,0.2)';ctx.fillRect(0,0,width,height);particles.forEach(p=>{p.update();p.draw();});requestAnimationFrame(animate);}
animate();
