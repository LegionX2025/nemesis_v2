
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('webgl-canvas'), alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        
        const geometry = new THREE.PlaneGeometry(100, 100, 32, 32);
        
        const material = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec2 vUv;
                varying float vElevation;
                uniform float uTime;
                void main() {
                    vUv = uv;
                    vec4 modelPosition = modelMatrix * vec4(position, 1.0);
                    float elevation = sin(modelPosition.x * 2.0 + uTime) * 0.5
                                    + sin(modelPosition.y * 2.0 + uTime) * 0.5;
                    modelPosition.z += elevation;
                    vElevation = elevation;
                    vec4 viewPosition = viewMatrix * modelPosition;
                    vec4 projectedPosition = projectionMatrix * viewPosition;
                    gl_Position = projectedPosition;
                }
            `,
            fragmentShader: `
                varying vec2 vUv;
                varying float vElevation;
                void main() {
                    vec3 color1 = vec3(0.85, 0.92, 1.0); // Deep Light blue
                    vec3 color2 = vec3(0.9, 0.85, 1.0); // Vibrant Light purple
                    vec3 color3 = vec3(1.0, 1.0, 1.0); // White
                    
                    vec3 mixColor = mix(color1, color2, vElevation * 1.5 + 0.5);
                    mixColor = mix(mixColor, color3, sin(vUv.x * 10.0) * 0.2);
                    
                    gl_FragColor = vec4(mixColor, 1.0);
                }
            `,
            uniforms: {
                uTime: { value: 0 }
            },
            wireframe: true,
            transparent: true,
            opacity: 0.15
        });
        
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = -Math.PI / 3;
        scene.add(plane);
        camera.position.z = 5;
        camera.position.y = 1;
        
        const clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            const elapsedTime = clock.getElapsedTime();
            material.uniforms.uTime.value = elapsedTime * 0.3;
            plane.rotation.z = elapsedTime * 0.05;
            renderer.render(scene, camera);
        }
        animate();
        
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    