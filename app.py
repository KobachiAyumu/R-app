import numpy as np
import pyvista as pv
from Bio.PDB import PDBParser, Superimposer

def align_and_visualize_pdbs(pdb_fixed_path, pdb_moving_path):
    """
    2つのPDBファイルを自動で位置合わせ（アライメント）し、
    重ね合わせた状態で3D表示します。
    """
    # 1. PDBファイルを解析するパーサーの準備
    parser = PDBParser(QUIET=True)
    
    # 2. 構造の読み込み
    print("PDBファイルを読み込んでいます...")
    struct_fixed = parser.get_structure("fixed_protein", pdb_fixed_path)
    struct_moving = parser.get_structure("moving_protein", pdb_moving_path)
    
    # 3. アライメントの基準となるCα（アルファ炭素）原子を抽出
    fixed_atoms = []
    moving_atoms = []
    
    for model in struct_fixed:
        for chain in model:
            for residue in chain:
                # 残基が標準的なアミノ酸であり、かつCα原子を持っている場合
                if "CA" in residue and residue.id[0] == " ":
                    fixed_atoms.append(residue["CA"])
                    
    for model in struct_moving:
        for chain in model:
            for residue in chain:
                if "CA" in residue and residue.id[0] == " ":
                    moving_atoms.append(residue["CA"])
    
    # 2つのファイルの原子数（アミノ酸残基数）が異なる場合、
    # 共通する最小限の長さでマッピングを行います
    num_atoms = min(len(fixed_atoms), len(moving_atoms))
    if num_atoms == 0:
        print("エラー: Cα原子が見つかりませんでした。PDBファイル形式を確認してください。")
        return
    
    fixed_subset = fixed_atoms[:num_atoms]
    moving_subset = moving_atoms[:num_atoms]
    
    print(f"基準点として {num_atoms} 個のCα原子を使用します。")
    
    # 4. スーパーインポーズ（最小二乗法による自動アライメント）の実行
    super_imposer = Superimposer()
    super_imposer.set_atoms(fixed_subset, moving_subset)
    
    # 移動側の構造全体に、計算された回転・平行移動を適用する
    super_imposer.apply(struct_moving.get_atoms())
    
    # ズレの度合いを示すRMSD（Å: オングストローム単位）を表示
    print(f"位置合わせが完了しました！")
    print(f"構造間のズレ（RMSD）: {super_imposer.rmsd:.4f} Å")
    
    # 5. 可視化データの作成（全原子の3D座標を抽出）
    coords_fixed = np.array([atom.coord for atom in struct_fixed.get_atoms()])
    coords_moving = np.array([atom.coord for atom in struct_moving.get_atoms()])
    
    # 6. PyVistaによる3Dレンダリング
    print("3D画面を起動しています...")
    plotter = pv.Plotter(window_size=[1000, 800])
    plotter.background_color = "white"  # 背景色を白に設定して見やすくする
    
    # 固定側モデル（赤色、半透明）
    mesh_fixed = pv.PolyData(coords_fixed)
    plotter.add_mesh(
        mesh_fixed, 
        color="#FF5733", 
        point_size=6, 
        opacity=0.6, 
        render_points_as_spheres=True, 
        label="Fixed Protein (Red)"
    )
    
    # 位置合わせ後の移動側モデル（青色、半透明）
    mesh_moving = pv.PolyData(coords_moving)
    plotter.add_mesh(
        mesh_moving, 
        color="#3370FF", 
        point_size=6, 
        opacity=0.6, 
        render_points_as_spheres=True, 
        label="Aligned Protein (Blue)"
    )
    
    # 画面の装飾
    plotter.add_legend(bcolor="white", size=(0.2, 0.15))
    plotter.add_axes()
    plotter.show_grid(color="gray", xtitle="X (Å)", ytitle="Y (Å)", ztitle="Z (Å)")
    
    # 表示の実行
    plotter.show()

# --- 実行部分 ---
if __name__ == "__main__":
    # ここにお手持ちのPDBファイル名を入力してください。
    # 例： "target.pdb"（動かさない基準）と "source.pdb"（自動で吸着させるデータ）
    pdb_file1 = "fixed_structure.pdb"
    pdb_file2 = "moving_structure.pdb"
    
    try:
        align_and_visualize_pdbs(pdb_file1, pdb_file2)
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません。パスが正しいか確認してください。\n{e}")