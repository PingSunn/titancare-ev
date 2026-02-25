import React from 'react';

const CarDisplay = ({ car, variantIdx, onVariantChange }) => {
  const currentVariant = car.Variants[variantIdx];

  const getImagePath = (imageName) => {
    return new URL(`../assets/${imageName}`, import.meta.url).href;
  };

  return (
    <div className="flex flex-col md:flex-row gap-10 items-start">
      
      {/* ฝั่งซ้าย: กล่องข้อมูล (Boxed Specs) */}
      <div className="w-full md:w-5/12 space-y-6">
        <div>
          <h2 className="text-4xl font-black text-gray-900 italic uppercase tracking-tighter">
            {car.Models}
          </h2>
          <div className="h-1 w-16 bg-[#cc0000] mt-4" />
        </div>

        {/* 1. กรอบเลือกรุ่นย่อย */}
        <div className="border border-gray-200 p-5 bg-white shadow-sm">
          <p className="text-[10px] text-gray-400 font-black mb-3 tracking-widest uppercase">Select Sub-Model</p>
          <div className="flex flex-wrap gap-2">
            {car.Variants.map((variant, i) => (
              <button
                key={i}
                onClick={() => onVariantChange(i)}
                className={`px-4 py-2 text-[11px] font-bold border transition-all ${
                  variantIdx === i 
                    ? 'bg-gray-900 border-gray-900 text-white' 
                    : 'bg-white border-gray-300 text-gray-500 hover:border-gray-900'
                }`}
              >
                {variant.Sub_model}
              </button>
            ))}
          </div>
        </div>

        {/* 2. กรอบราคาและสเปกหลัก (สไตล์ Honda) */}
        <div className="border-2 border-gray-900 p-6 bg-white space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-[10px] text-gray-400 font-bold uppercase">Starting Price</p>
              <p className="text-4xl font-black text-gray-900 italic">฿{currentVariant.Starting_price}</p>
            </div>
            <span className="bg-[#cc0000] text-white px-3 py-1 text-[10px] font-bold uppercase italic">
              {currentVariant.Sub_model}
            </span>
          </div>

          {/* PERFORMANCE BOX */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
            <SpecBox label="Range (NEDC)" value={currentVariant.PERFORMANCE.Range_km} />
            <SpecBox label="Battery" value={`${currentVariant.PERFORMANCE.Battery_Capacity_kWh} kWh`} />
            <SpecBox label="Max Power" value={`${currentVariant.PERFORMANCE.Max_Power_kW} kW`} />
            <SpecBox label="Acceleration" value={`${currentVariant.PERFORMANCE.Acceleration_0_100_s} s`} />
          </div>
        </div>

        {/* 3. กรอบข้อมูลตัวถัง (DIMENSIONS) */}
        <div className="border border-gray-200 p-5 bg-gray-50 grid grid-cols-2 gap-4">
           <SpecBox label="Dimensions (LxWxH)" value={currentVariant.DIMENSIONS.Size_LxWxH_mm} colSpan="col-span-2" />
           <SpecBox label="Wheelbase" value={`${currentVariant.DIMENSIONS.Wheelbase_mm} mm`} />
           <SpecBox label="Curb Weight" value={`${currentVariant.DIMENSIONS.Curb_Weight_Kg} kg`} />
        </div>
      </div>

      {/* ฝั่งขวา: รูปภาพรถใหญ่ */}
      <div className="w-full md:w-7/12 mt-10 md:mt-20">
        <div className="relative group">
          <img 
            key={`${car.Models}-${variantIdx}`}
            src={getImagePath(car.image)} 
            className="w-full object-contain drop-shadow-[0_35px_35px_rgba(0,0,0,0.2)] animate-slide-up"
            alt={car.Models}
          />
          {/* เงาสะท้อน */}
          <div className="w-3/4 h-6 bg-black/10 blur-2xl rounded-full mx-auto -mt-6" />
        </div>
      </div>
    </div>
  );
};

// Component ย่อยสำหรับกรอบข้อมูล
const SpecBox = ({ label, value, colSpan = "" }) => (
  <div className={`${colSpan}`}>
    <p className="text-[9px] text-gray-400 font-bold uppercase tracking-tight">{label}</p>
    <p className="text-sm font-black text-gray-800 italic uppercase">{value}</p>
  </div>
);

export default CarDisplay;