const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function generateFavicon() {
  // 使用更大的尺寸以保证清晰度
  const iconSize = 64;

  // 读取原始图片
  const inputPath = path.join(__dirname, '../src/assets/images/grt.png');
  const outputPath = path.join(__dirname, '../public/favicon.png');

  try {
    // 读取图片并处理颜色 - 将内容变为与TestHub相同的紫色
    const iconBuffer = await sharp(inputPath)
      .resize(iconSize, iconSize, { fit: 'contain' })
      .raw()
      .toBuffer({ resolveWithObject: true });

    // 创建紫色版本的图标，保持透明背景
    // 使用与TestHub文字相同的颜色 #5a32a3
    const purpleIcon = Buffer.alloc(iconSize * iconSize * 4);
    const { data, info } = iconBuffer;

    for (let i = 0; i < info.width * info.height; i++) {
      const idx = i * 4;
      const alpha = data[idx + 3];

      if (alpha > 128) { // 如果是图片内容（非透明）
        // 将内容变为与TestHub相同的紫色 #5a32a3
        purpleIcon[idx] = 90;      // R: 90
        purpleIcon[idx + 1] = 50;  // G: 50
        purpleIcon[idx + 2] = 163; // B: 163
        purpleIcon[idx + 3] = 255; // A: 不透明
      } else {
        // 透明区域保持透明
        purpleIcon[idx] = 0;
        purpleIcon[idx + 1] = 0;
        purpleIcon[idx + 2] = 0;
        purpleIcon[idx + 3] = 0;
      }
    }

    // 直接输出处理后的图标（透明背景）
    await sharp(purpleIcon, {
      raw: { width: iconSize, height: iconSize, channels: 4 }
    }).png().toFile(outputPath);

    console.log('Favicon with TestHub color (#5a32a3) and larger size created successfully!');
  } catch (error) {
    console.error('Error generating favicon:', error);
    process.exit(1);
  }
}

generateFavicon();
