import React, { useState, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react'; 
import CarDisplay from './components/CarDisplay';
import ChatWidget from './components/ChatWidget'; // เติมบรรทัดนี้
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
      scrollRef.current.scrollTo({
        left: direction === 'left' ? scrollLeft - 300 : scrollLeft + 300,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-100 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto w-full px-4 relative flex items-center group">
          
          <button onClick={() => scroll('left')} className="absolute left-0 z-10 p-2 bg-white/90 rounded-full border shadow-md opacity-0 group-hover:opacity-100 transition-opacity">
            <ChevronLeft size={24} className="text-gray-600" />
          </button>

          <div ref={scrollRef} className="flex items-center gap-12 overflow-x-auto no-scrollbar px-12 w-full scroll-smooth flex-nowrap">
            {carData.map((car, idx) => (
              <button
                key={car.Models}
                onClick={() => handleModelChange(idx)}
                className={`flex flex-col items-center min-w-[100px] transition-all duration-300 relative pb-2 ${
                  selectedIdx === idx ? 'opacity-100 scale-105' : 'opacity-40 grayscale hover:opacity-100 hover:grayscale-0'
                }`}
              >
                <img src={getImagePath(car.image)} alt={car.Models} className="h-14 w-auto object-contain mb-2" />
                
                <span className={`text-xs font-black uppercase whitespace-nowrap tracking-tight ${
                  selectedIdx === idx ? 'text-[#cc0000]' : 'text-gray-500'
                }`}>
                  {car.Models}
                </span>
                
                {selectedIdx === idx && <div className="absolute bottom-0 w-full h-[2px] bg-[#cc0000]" />}
              </button>
            ))}
          </div>

          <button onClick={() => scroll('right')} className="absolute right-0 z-10 p-2 bg-white/90 rounded-full border shadow-md opacity-0 group-hover:opacity-100 transition-opacity">
            <ChevronRight size={24} className="text-gray-600" />
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <CarDisplay car={carData[selectedIdx]} variantIdx={variantIdx} onVariantChange={setVariantIdx} />
      </main>

      <ChatWidget />

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slide-up {
          animation: slideUp 0.6s ease-out forwards;
        }
      `}} />
    </div>
  );
}