import React from 'react';

const CarDisplay = ({ car, variantIdx, onVariantChange }) => {
  const currentVariant = car.Variants[variantIdx];

  const getImagePath = (imageName) => {
    return new URL(`../assets/${imageName}`, import.meta.url).href;
  };

  return (
    <div className="flex flex-col md:flex-row gap-12 items-center md:items-start max-w-6xl mx-auto py-10">
      
      <div className="w-full md:w-[400px] space-y-5">
        <div>
          <h2 className="text-4xl font-black text-gray-900 italic uppercase leading-none tracking-tighter">
            {car.Models}
          </h2>
          <div className="h-1.5 w-12 bg-[#cc0000] mt-3" />
        </div>

        <div className="border border-gray-100 p-3 bg-white">
          <p className="text-[10px] text-gray-400 font-bold mb-2 tracking-widest uppercase">Select Sub-Model</p>
          <div className="flex flex-wrap gap-2">
            {car.Variants.map((variant, i) => (
              <button
                key={i}
                onClick={() => onVariantChange(i)}
                className={`px-4 py-2 text-[9px] font-black border transition-all ${
                  variantIdx === i 
                    ? 'bg-gray-900 text-white border-gray-900' 
                    : 'bg-white text-gray-500 border-gray-200 hover:border-gray-500'
                }`}
              >
                {variant.Sub_model}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 border-2 border-gray-900 bg-white">
          <p className="text-[10px] text-gray-400 font-bold uppercase mb-1">ราคาเริ่มต้น</p>
          <div className="flex justify-between items-end">
            <p className="text-4xl font-black text-gray-900 italic leading-none">
              <span className="text-sm mr-1 font-normal">฿</span>{currentVariant.Starting_price}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 p-4 border border-gray-100 bg-gray-50/50">
          <div>
            <p className="text-[9px] text-gray-400 font-bold uppercase tracking-tight">ระยะทางวิ่งสูงสุด</p>
            <p className="text-sm font-black italic uppercase mt-1">{currentVariant.PERFORMANCE.Range_km}</p>
          </div>
          <div>
            <p className="text-[9px] text-gray-400 font-bold uppercase tracking-tight">ความจุแบตเตอรี่</p>
            <p className="text-sm font-black italic uppercase mt-1">{currentVariant.PERFORMANCE.Battery_Capacity_kWh} kWh</p>
          </div>
          <div className="col-span-2 pt-2 border-t border-gray-100">
            <p className="text-[9px] text-gray-400 font-bold uppercase tracking-tight">ขนาดตัวถัง (LxWxH)</p>
            <p className="text-sm font-black italic uppercase mt-1">{currentVariant.DIMENSIONS.Size_LxWxH_mm}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex justify-center items-center py-4 w-full relative">
        <img 
          key={`${car.Models}-${variantIdx}`}
          src={getImagePath(car.image)} 
          alt={car.Models}
          className="w-full max-w-[650px] object-contain drop-shadow-[0_20px_40px_rgba(0,0,0,0.15)] animate-slide-up relative z-10"
        />
        <div className="absolute bottom-6 w-[70%] h-6 bg-black/10 blur-xl rounded-full mx-auto" />
      </div>
    </div>
  );
};

export default CarDisplay;