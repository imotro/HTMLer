const container = document.querySelector('div#app');
  let move = (e) => {
  const x = e.clientX;
  const y = e.clientY;

  const element = document.createElement('div');
  element.style.position = 'absolute';
  element.style.top = `${y}px`;
  element.style.left = `${x}px`;
  element.style.width = '20px';
  element.style.height = '20px';
  element.style.background = 'red';
  element.style.opacity = '50%'
  element.style.borderRadius = '15px'
  element.id = 'mouse'
  try{document.querySelector('div#mouse').remove()}catch(err){console.log(err)}

  container.appendChild(element);
}

container.addEventListener('mousemove', move)