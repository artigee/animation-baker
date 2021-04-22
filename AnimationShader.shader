Shader "Unlit/AnimationShader"
{
    Properties
    {
        _MainTex("MainTexture", 2D) = "white" {}
        _AnimTex("AnimationTexture", 2D) = "white" {}
        _Frames("Frames", int) = 1
        _FrameWidth("FrameWidth", int) = 1
        _AnimationOffset("AnimationOffset", int) = 0
        _Speed("Speed", float) = 100
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
                float2 uv2 : TEXCOORD1;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            sampler2D _AnimTex;
            float4 _AnimTex_TexelSize;
            int _Frames;
            int _FrameWidth;
            int _AnimationOffset;
            float _Speed;

            float GetTime() 
            {
                return _Time.x * _Speed;
            }

            fixed4 GetColorAt(float2 uv2, int frameOffset)
            {
                int time = floor(GetTime());
                int frame = time % (_Frames - 1) + frameOffset;
                float xs = (frame + _AnimationOffset) * _FrameWidth * _AnimTex_TexelSize.x + uv2.x;
                fixed4 start = tex2Dlod(_AnimTex, float4(xs, uv2.y, 0, 0));
                return start;
            }
            fixed3 Convert(fixed4 input)
            {
                int alpha = floor(input.a * 255.0);
                int3 rgb2 = int3(alpha >> 6 & 0x03, alpha >> 4 & 0x03, alpha >> 2 & 0x03);
                int w = (alpha & 0x03) * 2 + 1;
                int3 rgbw = rgb2 - 2;
                fixed3 c = rgbw + input.xyz;
                fixed3 sub = c * w;
                return -sub;
            }

            float4 GetVertexOffset(appdata v)
            {
                fixed3 dv = Convert(GetColorAt(v.uv2, 0));
                return float4(-dv.x, dv.z, -dv.y, 0);
            }

            v2f vert(appdata v)
            {
                v2f o;
                v.vertex += GetVertexOffset(v);
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }


            fixed4 frag(v2f i) : SV_Target
            {
                fixed4 col = tex2D(_MainTex, i.uv);
                return col;
            }
            ENDCG
        }
    }
}
