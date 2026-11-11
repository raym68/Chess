const symbols={K:['♔','♚'],Q:['♕','♛'],R:['♖','♜'],B:['♗','♝'],N:['♘','♞'],P:['♙','♟'],G:['G','G'],C:['C','C'],E:['E','E']};
const customIcons={G:'icons/griffin.svg',C:'icons/camel.svg',E:'icons/elephant.svg'};
const names={B:'Слон',G:'Грифон',C:'Верблюд',E:'Прыгающий слон',Q:'Ферзь',R:'Ладья',N:'Конь'};
const board=document.querySelector('#board'), statusEl=document.querySelector('#status');
let state=null, selected=null, moves=[];
for(const side of ['top','bottom']){const axis=document.querySelector(`#files-${side}`);for(const file of 'abcdefgh'){const label=document.createElement('span');label.textContent=file;axis.append(label);}}
for(const side of ['left','right']){const axis=document.querySelector(`#ranks-${side}`);for(let rank=8;rank>=1;rank--){const label=document.createElement('span');label.textContent=rank;axis.append(label);}}
async function api(path,data){const response=await fetch(path,{method:data?'POST':'GET',headers:{'Content-Type':'application/json'},body:data?JSON.stringify(data):undefined});const value=await response.json();if(!response.ok)throw Error(value.error||'Ошибка сервера');return value;}
function setup(options, slots, selected){
  const group=document.querySelector('#setup');group.replaceChildren();
  for(const index of slots){
    const file='abcdefgh'[index];
    const select=document.createElement('select');select.id=`piece-${index}`;
    select.setAttribute('aria-label',`Фигура на линии ${file} для обеих сторон`);
    for(const optionData of options){
      const option=document.createElement('option');option.value=optionData.kind;
      option.textContent=`${file}: ${optionData.name}`;select.append(option);
    }
    select.value=selected[index];
    const preview=document.createElement('span');preview.className='setup-preview';
    const refresh=()=>{
      preview.replaceChildren();
      if(customIcons[select.value]){
        const img=document.createElement('img');img.src=customIcons[select.value];
        img.alt=names[select.value];preview.append(img);
      }else preview.textContent=symbols[select.value][0];
    };
    select.addEventListener('change',refresh);refresh();
    const row=document.createElement('div');row.className='setup-row';row.append(select,preview);group.append(row);
  }
}
function pieceNode(piece){const span=document.createElement('span');span.className=`piece ${piece.color} ${'GCE'.includes(piece.kind)?'custom':''}`;if(customIcons[piece.kind]){const img=document.createElement('img');img.src=customIcons[piece.kind];img.alt=names[piece.kind];span.append(img);}else span.textContent=symbols[piece.kind][piece.color==='white'?0:1];span.title=`${piece.color==='white'?'Белые':'Чёрные'}: ${names[piece.kind]||piece.kind}`;return span;}
function render(){const tbody=document.querySelector('#history tbody');tbody.replaceChildren();for(let i=0;i<state.history.length;i+=2){const row=document.createElement('tr');for(const value of [String(i/2+1)+'.',state.history[i],state.history[i+1]||'']){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}tbody.append(row);}tbody.parentElement.parentElement.scrollTop=tbody.parentElement.parentElement.scrollHeight;board.replaceChildren();statusEl.textContent=`${state.status} · ходят ${state.turn==='white'?'белые':'чёрные'}`;for(let r=0;r<8;r++)for(let c=0;c<8;c++){const button=document.createElement('button');button.className=`square ${(r+c)%2?'dark':''}`;button.setAttribute('aria-label',`${'abcdefgh'[c]}${8-r}`);const piece=state.board[r][c];if(piece)button.append(pieceNode(piece));if(state.checked_king&&state.checked_king[0]===r&&state.checked_king[1]===c)button.classList.add('check');if(selected&&selected[0]===r&&selected[1]===c)button.classList.add('selected');if(moves.some(([mr,mc])=>mr===r&&mc===c))button.classList.add('legal',piece?'capture':'empty');button.onclick=()=>clickSquare(r,c);board.append(button);}if(state.promotion){const dialog=document.querySelector('#promotion'), choices=document.querySelector('#choices');choices.replaceChildren();for(const kind of state.promotion_options){const button=document.createElement('button');if(customIcons[kind]){const img=document.createElement('img');img.src=customIcons[kind];img.alt='';button.append(img);}else{const symbol=document.createElement('span');symbol.textContent=symbols[kind][state.turn==='white'?0:1];button.append(symbol);}button.append(document.createTextNode(` ${names[kind]}`));button.onclick=async()=>{try{state=await api('/api/promote',{kind});dialog.close();render();}catch(e){alert(e.message)}};choices.append(button)}if(!dialog.open)dialog.showModal();}}
async function clickSquare(r,c){if(state.promotion)return;try{if(selected&&moves.some(([mr,mc])=>mr===r&&mc===c)){state=await api('/api/move',{start:selected,end:[r,c]});selected=null;moves=[];render();return}const piece=state.board[r][c];if(piece&&piece.color===state.turn){selected=[r,c];moves=(await api(`/api/moves?r=${r}&c=${c}`)).moves;}else{selected=null;moves=[];}render();}catch(e){alert(e.message)}}
document.querySelector('#new').onclick=async()=>{const back_rank=[...state.back_rank];for(const index of state.setup_slots)back_rank[index]=document.getElementById(`piece-${index}`).value;try{state=await api('/api/new',{back_rank});selected=null;moves=[];render()}catch(e){alert(e.message)}};
document.querySelector('#theme').onchange=e=>{document.body.dataset.theme=e.target.value;localStorage.setItem('chess-theme',e.target.value)};
document.body.dataset.theme=localStorage.getItem('chess-theme')||'wood';document.querySelector('#theme').value=document.body.dataset.theme;
api('/api/state').then(s=>{state=s;setup(s.setup_options,s.setup_slots,s.back_rank);render()}).catch(e=>{statusEl.textContent=e.message});
