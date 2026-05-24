import React, { useState } from "react";
import ImageTracer from "imagetracerjs";

const ImageToSVG = () => {
  const [image, setImage] = useState(null);
  const [svg, setSvg] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = () => {
      setImage(reader.result);
    };

    reader.readAsDataURL(file);
  };

  const convertToSVG = () => {
    if (!image) return;

    setLoading(true);

    ImageTracer.imageToSVG(
      image,
      (svgString) => {
        setSvg(svgString);
        setLoading(false);
      },
      {
        ltres: 1,
        qtres: 1,
        pathomit: 8,
        colorsampling: 2,
      }
    );
  };

  const downloadSVG = () => {
    const blob = new Blob([svg], { type: "image/svg+xml" });

    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = "converted-image.svg";

    link.click();
  };

  return (
    <div className="min-h-screen p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">
        PNG/JPG to SVG Converter
      </h1>

      <input
        type="file"
        accept="image/png, image/jpeg"
        onChange={handleUpload}
        className="mb-4"
      />

      {image && (
        <img
          src={image}
          alt="preview"
          className="w-64 rounded-lg shadow-lg mb-4"
        />
      )}

      <button
        onClick={convertToSVG}
        className="bg-blue-500 text-white px-6 py-2 rounded-lg mb-6"
      >
        Convert to SVG
      </button>

      {loading && <p>Generating SVG...</p>}

      {svg && (
        <div className="w-full max-w-2xl">
          <div
            className="border p-4 rounded-lg bg-white"
            dangerouslySetInnerHTML={{ __html: svg }}
          />

          <button
            onClick={downloadSVG}
            className="mt-4 bg-green-500 text-white px-6 py-2 rounded-lg"
          >
            Download SVG
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageToSVG;