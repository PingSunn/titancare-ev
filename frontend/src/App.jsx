import React, { useState, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react'; 
import CarDisplay from './components/CarDisplay';
import ChatWidget from './components/ChatWidget';
import carData from './data/cars.json';

export default function App() {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [variantIdx, setVariantIdx] = useState(0);
  const scrollRef = useRef(null);

  const getImagePath = (imageName) => {
    return new URL(`./assets/${imageName}`, import.meta.url).href;
  };

  const handleModelChange = (idx) => {
    setSelectedIdx(idx);
    setVariantIdx(0);
  };

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft } = scrollRef.current;
      const scrollAmount = 200;
      scrollRef.current.scrollTo({
        left: direction === 'left' ? scrollLeft - scrollAmount : scrollLeft + scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* ส่วนแถบเลือกรถที่เล็กและเป็นคอลัมน์เดียว */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-5xl mx-auto px-2 relative flex items-center group">
          
          {/* ปุ่มลูกศรซ้าย (จิ๋ว) */}
          <button 
            onClick={() => scroll('left')}
            className="absolute left-0 z-10 p-0.5 bg-white/90 rounded-full border shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <ChevronLeft size={14} />
          </button>

          {/* รายการรถ - flex-nowrap บังคับแถวเดียวแน่นอน */}
          <div 
            ref={scrollRef}
            className="flex items-center gap-4 overflow-x-auto no-scrollbar py-2 px-6 scroll-smooth flex-nowrap w-full"
          >
            {carData.map((car, idx) => (
              <button
                key={car.Models}
                onClick={() => handleModelChange(idx)}
                className={`flex flex-col items-center justify-center min-w-[60px] transition-all duration-300 relative ${
                  selectedIdx === idx ? 'opacity-100' : 'opacity-30 grayscale hover:opacity-80'
                }`}
              >
                {/* รูปรถขนาดจิ๋วมาก (h-5 คือ 20px) */}
                <img 
                  src={getImagePath(car.image)} 
                  alt={car.Models}
                  className="h-5 w-auto object-contain mb-0.5" 
                />
                <span className={`text-[7px] font-black uppercase tracking-tighter whitespace-nowrap ${
                  selectedIdx === idx ? 'text-[#cc0000]' : 'text-gray-400'
                }`}>
                  {car.Models}
                </span>
                
                {/* ขีดเส้นใต้แบบ Micro */}
                {selectedIdx === idx && (
                  <div className="absolute -bottom-2 w-full h-[1.5px] bg-[#cc0000]" />
                )}
              </button>
            ))}
          </div>

          {/* ปุ่มลูกศรขวา (จิ๋ว) */}
          <button 
            onClick={() => scroll('right')}
            className="absolute right-0 z-10 p-0.5 bg-white/90 rounded-full border shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </nav>

      {/* เนื้อหาหลัก */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <CarDisplay 
          car={carData[selectedIdx]} 
          variantIdx={variantIdx} 
          onVariantChange={setVariantIdx} 
        />
      </main>

      <ChatWidget />
    </div>
  );
}